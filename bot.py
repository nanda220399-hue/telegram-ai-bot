import telebot
import requests
import os
import json
import time

# =========================
# CONFIG
# =========================

TOKEN = "8033529702:AAENz15QMaIBja_soQa7yyHw02xaVw1RCW0"
HF_TOKEN = "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"
REPLICATE_API = "r8_Lp5PPCCsYU7sxcFwqkYYZAjDWvMPE9I26vXVv"

bot = telebot.TeleBot(TOKEN)

DB = "users.json"

# =========================
# DATABASE
# =========================

def load_users():

    if not os.path.exists(DB):
        return {}

    return json.load(open(DB))


def save_users(data):

    json.dump(data,open(DB,"w"))


users = load_users()


def register(uid):

    uid = str(uid)

    if uid not in users:

        users[uid] = {
            "step":"product",
            "style":None
        }

        save_users(users)

# =========================
# START
# =========================

@bot.message_handler(commands=['start'])

def start(m):

    uid = str(m.from_user.id)

    register(uid)

    users[uid]["step"] = "product"

    save_users(users)

    bot.send_message(
        m.chat.id,
        "STEP 1\nUpload foto PRODUK"
    )


# =========================
# HANDLE PHOTO
# =========================

@bot.message_handler(content_types=['photo'])

def photo(m):

    uid = str(m.from_user.id)

    step = users[uid]["step"]

    file = bot.get_file(m.photo[-1].file_id)

    img = bot.download_file(file.file_path)

    if step == "product":

        open("product.jpg","wb").write(img)

        users[uid]["step"] = "face"

        save_users(users)

        bot.send_message(
            m.chat.id,
            "STEP 2\nUpload foto WAJAH"
        )

        return


    if step == "face":

        open("face.jpg","wb").write(img)

        users[uid]["step"] = "style"

        save_users(users)

        bot.send_message(
            m.chat.id,
            """
Pilih style

1 OOTD
2 UGC
3 POV
4 Dance
"""
        )


# =========================
# STYLE SELECT
# =========================

@bot.message_handler(func=lambda m: m.text in ["1","2","3","4"])

def style(m):

    uid = str(m.from_user.id)

    users[uid]["style"] = m.text

    save_users(users)

    bot.send_message(m.chat.id,"AI processing...")

    generate_model(m.chat.id,m.text)


# =========================
# GENERATE MODEL
# =========================

def generate_model(chat,style):

    style_map = {

        "1":"fashion influencer ootd",

        "2":"ugc product review influencer",

        "3":"pov product advertisement",

        "4":"tiktok dance influencer"

    }

    prompt = f"""
photo of a female influencer

style {style_map[style]}

studio lighting
social media advertisement
high quality
"""

    API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }

    payload = {
        "inputs": prompt
    }

    bot.send_message(chat,"AI membuat model influencer...")

    r = requests.post(API_URL,headers=headers,json=payload)

    if r.status_code != 200:

        bot.send_message(chat,f"AI model error:\n{r.text}")

        return

    open("model.jpg","wb").write(r.content)

    face_swap(chat)


# =========================
# FACE SWAP
# =========================

def face_swap(chat):

    bot.send_message(chat,"AI face swap sedang diproses...")

    url = "https://api.replicate.com/v1/predictions"

    headers = {
        "Authorization": f"Token {REPLICATE_API}",
        "Content-Type": "application/json"
    }

    data = {
        "version":"7de2ea26f2e6b5b2c48dfc1baf7a0b4f2d0e8d6d3a7b8b1b3a6d2a1f7a9d9f1",
        "input":{
            "source_image":"face.jpg",
            "target_image":"model.jpg"
        }
    }

    r = requests.post(url,json=data,headers=headers)

    prediction = r.json()

    get_url = prediction["urls"]["get"]

    while True:

        r = requests.get(get_url,headers=headers)

        result = r.json()

        if result["status"] == "succeeded":

            image_url = result["output"]

            break

        if result["status"] == "failed":

            bot.send_message(chat,"Face swap gagal")

            return

        time.sleep(2)

    img = requests.get(image_url).content

    open("result.png","wb").write(img)

    bot.send_photo(chat,open("result.png","rb"))

    bot.send_message(chat,"Selesai.\nKetik /start untuk membuat lagi.")


# =========================
# RUN BOT
# =========================

print("BOT RUNNING")

bot.infinity_polling()
