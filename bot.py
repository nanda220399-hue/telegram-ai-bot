import telebot
import requests
import json
import os
from PIL import Image

TOKEN = "8033529702:AAENz15QMaIBja_soQa7yyHw02xaVw1RCW0"
GEMINI_API = "AIzaSyBvn61VrlVZKcKu_OP2GmcFRRoWkEjNePM"

bot = telebot.TeleBot(TOKEN)

DB="users.json"

# ================= DATABASE =================

def load():
    if not os.path.exists(DB):
        return {}
    return json.load(open(DB))

def save(data):
    json.dump(data,open(DB,"w"))

users=load()

def register(uid):

    uid=str(uid)

    if uid not in users:

        users[uid]={
            "limit":5,
            "plan":"free",
            "step":"none",
            "product":None,
            "face":None,
            "style":None
        }

        save(users)

# ================= START =================

@bot.message_handler(commands=['start'])
def start(m):

    register(m.from_user.id)

    bot.send_message(m.chat.id,
"""
AI AFFILIATE CREATOR

Upload foto produk dulu.
""")

    users[str(m.from_user.id)]["step"]="product"

    save(users)

# ================= LIMIT =================

@bot.message_handler(commands=['limit'])
def limit(m):

    register(m.from_user.id)

    bot.send_message(m.chat.id,
    f"Limit: {users[str(m.from_user.id)]['limit']}")

# ================= STYLE =================

def style_menu(chat):

    bot.send_message(chat,
"""
Pilih Style:

1 OOTD
2 Dance Smooth
3 UGC Review
4 Affiliate Photo
""")

# ================= PHOTO =================

@bot.message_handler(content_types=['photo'])
def photo(m):

    uid=str(m.from_user.id)

    register(uid)

    user=users[uid]

    if user["limit"]<=0:

        bot.send_message(m.chat.id,"Limit habis /upgrade")

        return

    file=bot.get_file(m.photo[-1].file_id)

    img=bot.download_file(file.file_path)

    if user["step"]=="product":

        open("product.jpg","wb").write(img)

        users[uid]["product"]="product.jpg"

        users[uid]["step"]="face"

        save(users)

        bot.send_message(m.chat.id,
        "Sekarang upload foto wajah / model")

        return

    if user["step"]=="face":

        open("face.jpg","wb").write(img)

        users[uid]["face"]="face.jpg"

        users[uid]["step"]="style"

        save(users)

        style_menu(m.chat.id)

# ================= STYLE SELECT =================

@bot.message_handler(func=lambda m: m.text in ["1","2","3","4"])
def style(m):

    uid=str(m.from_user.id)

    users[uid]["style"]=m.text

    save(users)

    bot.send_message(m.chat.id,"AI sedang membuat konten...")

    generate(m)

# ================= GENERATE =================

def generate(m):

    uid=str(m.from_user.id)

    style_map={
    "1":"OOTD influencer wearing product",
    "2":"tiktok dance holding product",
    "3":"UGC product review",
    "4":"affiliate product showcase"
    }

    style=style_map[users[uid]["style"]]

    prompt=f"""
Create affiliate marketing content.

Style: {style}

Make 3 scenes video idea.

Include script and caption.
"""

    url=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API}"

    data={
    "contents":[
        {"parts":[{"text":prompt}]}
    ]
    }

    r=requests.post(url,json=data)

    res=r.json()

    try:

        text=res["candidates"][0]["content"]["parts"][0]["text"]

    except:

        text="AI error"

    bot.send_message(m.chat.id,text)

    users[uid]["limit"]-=1

    users[uid]["step"]="product"

    save(users)

    bot.send_message(m.chat.id,"Upload produk baru untuk generate lagi.")

# ================= UPGRADE =================

@bot.message_handler(commands=['upgrade'])
def up(m):

    bot.send_message(m.chat.id,
"""
PLAN

Pro 100 generate
Agency unlimited

Hubungi admin.
""")

# ================= ADMIN =================

ADMIN=123456789

@bot.message_handler(commands=['addpro'])
def addpro(m):

    if m.from_user.id!=ADMIN:
        return

    uid=m.text.split()[1]

    users[uid]["limit"]=100
    users[uid]["plan"]="pro"

    save(users)

    bot.send_message(m.chat.id,"User upgraded")

# ================= RUN =================

print("BOT RUNNING")

bot.infinity_polling()

# =====================
# HANDLE STYLE
# =====================

@bot.message_handler(func=lambda m: m.text in ["1","2","3"])
def set_style(message):

    style_map = {
        "1":"OOTD influencer",
        "2":"Dance smooth tiktok",
        "3":"UGC product review"
    }

    bot.send_message(message.chat.id,f"Style dipilih: {style_map[message.text]}")



# =====================
# HANDLE FOTO
# =====================

@bot.message_handler(content_types=['photo'])
def handle_photo(message):

    user_id = str(message.from_user.id)

    register_user(user_id)

    user = users[user_id]

    if user["limit"] <= 0:

        bot.reply_to(message,"Limit habis. Ketik /upgrade")

        return


    bot.reply_to(message,"Foto diterima... AI sedang memproses")

    file_info = bot.get_file(message.photo[-1].file_id)

    downloaded = bot.download_file(file_info.file_path)

    with open("image.jpg","wb") as f:
        f.write(downloaded)



    prompt = """
Create a tiktok affiliate video concept.

Style: influencer
Camera: cinematic
Lighting: soft light

Explain the scene.
"""


    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API}"

    data = {
        "contents":[
            {"parts":[{"text":prompt}]}
        ]
    }

    headers = {
        "Content-Type":"application/json"
    }


    r = requests.post(url,headers=headers,json=data)

    result = r.text

    bot.send_message(message.chat.id,result)


    users[user_id]["limit"] -= 1

    save_users(users)



# =====================
# ADMIN COMMAND
# =====================

ADMIN_ID = 123456789


@bot.message_handler(commands=['addpro'])
def add_pro(message):

    if message.from_user.id != ADMIN_ID:
        return

    try:

        user_id = message.text.split()[1]

        users[user_id] = {
            "limit":100,
            "plan":"pro"
        }

        save_users(users)

        bot.reply_to(message,"User upgraded")

    except:

        bot.reply_to(message,"Format: /addpro USERID")



# =====================
# RUN BOT
# =====================

print("Bot Running...")

bot.polling()
