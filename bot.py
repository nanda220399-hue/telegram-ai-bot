import telebot
import os
import json

TOKEN="8033529702:AAENz15QMaIBja_soQa7yyHw02xaVw1RCW0"

bot=telebot.TeleBot(TOKEN)

DB="users.json"

# ================= DATABASE =================

def load_users():

    if not os.path.exists(DB):

        return {}

    return json.load(open(DB))


def save_users(data):

    json.dump(data,open(DB,"w"))


users=load_users()


def register(uid):

    uid=str(uid)

    if uid not in users:

        users[uid]={

            "step":"product",
            "style":None

        }

        save_users(users)


# ================= START =================

@bot.message_handler(commands=['start'])

def start(m):

    uid=str(m.from_user.id)

    register(uid)

    users[uid]["step"]="product"

    save_users(users)

    bot.send_message(m.chat.id,

    "STEP 1\nUpload foto PRODUK")


# ================= PHOTO =================

@bot.message_handler(content_types=['photo'])

def photo(m):

    uid=str(m.from_user.id)

    step=users[uid]["step"]

    file=bot.get_file(m.photo[-1].file_id)

    img=bot.download_file(file.file_path)


    if step=="product":

        open("product.jpg","wb").write(img)

        users[uid]["step"]="face"

        save_users(users)

        bot.send_message(m.chat.id,

        "STEP 2\nUpload foto WAJAH")

        return


    if step=="face":

        open("face.jpg","wb").write(img)

        users[uid]["step"]="style"

        save_users(users)

        bot.send_message(m.chat.id,

        """
Pilih style

1 OOTD
2 UGC
3 POV
4 Dance
""")


# ================= STYLE =================

@bot.message_handler(func=lambda m: m.text in ["1","2","3","4"])

def style(m):

    uid=str(m.from_user.id)

    users[uid]["style"]=m.text

    save_users(users)

    bot.send_message(m.chat.id,

    "Data diterima.\nAI processing akan dibuat di step berikutnya.")


print("BOT RUNNING")

bot.infinity_polling()
