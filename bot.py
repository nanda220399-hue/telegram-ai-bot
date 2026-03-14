import telebot
import requests
import os

# =============================
# CONFIG
# =============================

TOKEN = "8033529702:AAENz15QMaIBja_soQa7yyHw02xaVw1RCW0"
HF_TOKEN = "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"

bot = telebot.TeleBot(TOKEN)

user_state = {}

# =============================
# START
# =============================

@bot.message_handler(commands=['start'])
def start(message):

    bot.send_message(
        message.chat.id,
        """
AI AFFILIATE CREATOR

Upload foto PRODUK dulu
"""
    )

    user_state[message.chat.id] = {"step":"product"}


# =============================
# STYLE MENU
# =============================

def style_menu(chat):

    bot.send_message(
        chat,
        """
Pilih style konten

1 OOTD outfit
2 UGC review
3 POV product
4 Dance smooth
"""
    )


# =============================
# HANDLE PHOTO
# =============================

@bot.message_handler(content_types=['photo'])
def photo(message):

    chat = message.chat.id

    if chat not in user_state:
        return

    step = user_state[chat]["step"]

    file_info = bot.get_file(message.photo[-1].file_id)

    downloaded = bot.download_file(file_info.file_path)

    if step == "product":

        with open("product.jpg","wb") as f:
            f.write(downloaded)

        user_state[chat]["step"] = "face"

        bot.send_message(chat,"Upload foto WAJAH kamu")

        return

    if step == "face":

        with open("face.jpg","wb") as f:
            f.write(downloaded)

        user_state[chat]["step"] = "style"

        style_menu(chat)


# =============================
# STYLE SELECT
# =============================

@bot.message_handler(func=lambda m: m.text in ["1","2","3","4"])
def style(message):

    chat = message.chat.id

    style_map = {
        "1":"fashion ootd influencer wearing product",
        "2":"ugc product review holding product",
        "3":"pov holding product cinematic",
        "4":"tiktok dance holding product"
    }

    prompt = f"""
Photo of a person holding a product.

Style: {style_map[message.text]}

Realistic lighting
social media advertisement
"""

    bot.send_message(chat,"AI sedang membuat gambar...")

    generate_image(chat,prompt)


# =============================
# GENERATE IMAGE
# =============================

def generate_image(chat,prompt):

    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }

    payload = {
        "inputs": prompt
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:

        bot.send_message(chat,"AI error")

        return

    with open("result.png","wb") as f:
        f.write(response.content)

    bot.send_photo(chat,open("result.png","rb"))

    bot.send_message(chat,"Upload produk lagi untuk membuat konten baru")


# =============================
# RUN
# =============================

print("BOT RUNNING")

bot.infinity_polling()
