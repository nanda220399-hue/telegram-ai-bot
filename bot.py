import telebot
import requests
import json
import os

TOKEN = "8033529702:AAENz15QMaIBja_soQa7yyHw02xaVw1RCW0"
GEMINI_API = "AIzaSyBvn61VrlVZKcKu_OP2GmcFRRoWkEjNePM"

bot = telebot.TeleBot(TOKEN)

DB_FILE = "users.json"


# =====================
# DATABASE SIMPLE
# =====================

def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE,"r") as f:
        return json.load(f)

def save_users(data):
    with open(DB_FILE,"w") as f:
        json.dump(data,f)

users = load_users()


def register_user(user_id):

    if str(user_id) not in users:
        users[str(user_id)] = {
            "limit":3,
            "plan":"free"
        }
        save_users(users)


# =====================
# START COMMAND
# =====================

@bot.message_handler(commands=['start'])
def start(message):

    register_user(message.from_user.id)

    text = """
Welcome AI Affiliate Bot

Upload foto produk untuk membuat konten affiliate.

Commands:

/style
/limit
/upgrade
"""

    bot.reply_to(message,text)


# =====================
# CEK LIMIT
# =====================

@bot.message_handler(commands=['limit'])
def check_limit(message):

    user = users[str(message.from_user.id)]

    bot.reply_to(message,f"Limit kamu: {user['limit']}")


# =====================
# STYLE MENU
# =====================

@bot.message_handler(commands=['style'])
def style(message):

    text = """
Pilih style konten:

1 - OOTD
2 - Dance Smooth
3 - UGC Review

Ketik angka style.
"""

    bot.reply_to(message,text)


# =====================
# UPGRADE
# =====================

@bot.message_handler(commands=['upgrade'])
def upgrade(message):

    text = """
Upgrade plan:

Pro = 100 generate
Agency = unlimited

Hubungi admin untuk upgrade.
"""

    bot.reply_to(message,text)


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
