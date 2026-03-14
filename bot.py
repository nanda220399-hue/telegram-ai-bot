import telebot
import requests
import json
import os

# =============================
# CONFIG
# =============================

TOKEN = "8033529702:AAENz15QMaIBja_soQa7yyHw02xaVw1RCW0"
GEMINI_API = "AIzaSyBvn61VrlVZKcKu_OP2GmcFRRoWkEjNePM"

bot = telebot.TeleBot(TOKEN)

DB = "users.json"


# =============================
# DATABASE
# =============================

def load_users():
    if not os.path.exists(DB):
        return {}

    with open(DB, "r") as f:
        return json.load(f)


def save_users(data):
    with open(DB, "w") as f:
        json.dump(data, f)


users = load_users()


def register_user(uid):

    uid = str(uid)

    if uid not in users:

        users[uid] = {
            "limit": 5,
            "plan": "free",
            "step": "product",
            "style": None
        }

        save_users(users)


# =============================
# START
# =============================

@bot.message_handler(commands=['start'])
def start(message):

    register_user(message.from_user.id)

    bot.send_message(
        message.chat.id,
        """
AI AFFILIATE CREATOR BOT

STEP 1
Upload foto PRODUK dulu
"""
    )


# =============================
# LIMIT
# =============================

@bot.message_handler(commands=['limit'])
def limit(message):

    uid = str(message.from_user.id)

    register_user(uid)

    bot.send_message(
        message.chat.id,
        f"Limit kamu: {users[uid]['limit']}"
    )


# =============================
# UPGRADE
# =============================

@bot.message_handler(commands=['upgrade'])
def upgrade(message):

    bot.send_message(
        message.chat.id,
        """
PLAN

Pro = 100 generate
Agency = unlimited

Hubungi admin untuk upgrade
"""
    )


# =============================
# STYLE MENU
# =============================

def style_menu(chat_id):

    bot.send_message(
        chat_id,
        """
Pilih style konten:

1 OOTD
2 Dance Smooth
3 UGC Review
4 Affiliate Showcase
"""
    )


# =============================
# HANDLE PHOTO
# =============================

@bot.message_handler(content_types=['photo'])
def handle_photo(message):

    uid = str(message.from_user.id)

    register_user(uid)

    user = users[uid]

    if user["limit"] <= 0:

        bot.send_message(message.chat.id, "Limit habis. Ketik /upgrade")

        return

    file_info = bot.get_file(message.photo[-1].file_id)

    downloaded = bot.download_file(file_info.file_path)

    with open("product.jpg", "wb") as f:
        f.write(downloaded)

    users[uid]["step"] = "style"

    save_users(users)

    bot.send_message(message.chat.id, "Produk diterima")

    style_menu(message.chat.id)


# =============================
# STYLE SELECT
# =============================

@bot.message_handler(func=lambda m: m.text in ["1","2","3","4"])
def style_select(message):

    uid = str(message.from_user.id)

    users[uid]["style"] = message.text

    save_users(users)

    bot.send_message(message.chat.id, "AI sedang membuat konten...")

    generate_content(message)


# =============================
# GENERATE AI
# =============================

def generate_content(message):

    uid = str(message.from_user.id)

    style_map = {
        "1": "OOTD influencer wearing the product",
        "2": "TikTok dance holding product",
        "3": "UGC product review style",
        "4": "Affiliate product showcase"
    }

    style = style_map[users[uid]["style"]]

    prompt = f"""
Create a TikTok affiliate marketing video concept.

Style: {style}

Write:

1 Hook
3 Scenes
Caption
Call to action
"""

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={GEMINI_API}"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    result = response.json()

    try:

        text = result["candidates"][0]["content"]["parts"][0]["text"]

    except:

        text = str(result)

    bot.send_message(message.chat.id, text)

    users[uid]["limit"] -= 1

    save_users(users)

    bot.send_message(message.chat.id, "Upload produk lagi untuk generate baru.")


# =============================
# ADMIN UPGRADE
# =============================

ADMIN_ID = 123456789


@bot.message_handler(commands=['addpro'])
def add_pro(message):

    if message.from_user.id != ADMIN_ID:
        return

    try:

        user_id = message.text.split()[1]

        users[user_id]["limit"] = 100
        users[user_id]["plan"] = "pro"

        save_users(users)

        bot.send_message(message.chat.id, "User upgraded")

    except:

        bot.send_message(message.chat.id, "Format: /addpro USERID")


# =============================
# RUN BOT
# =============================

print("BOT RUNNING")

bot.infinity_polling()
