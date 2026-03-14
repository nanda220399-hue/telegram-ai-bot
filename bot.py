import telebot
import requests

TOKEN = "8033529702:AAENz15QMaIBja_soQa7yyHw02xaVw1RCW0"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Upload foto produk untuk generate konten affiliate")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):

    bot.reply_to(message, "Foto diterima, sedang diproses AI...")

    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open("image.jpg", "wb") as new_file:
        new_file.write(downloaded_file)

    bot.reply_to(message, "AI sedang membuat konsep video...")

bot.polling()
