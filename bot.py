import telebot

TOKEN = "8033529702:AAENz15QMaIBja_soQa7yyHw02xaVw1RCW0"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Upload foto produk untuk membuat video affiliate")

@bot.message_handler(content_types=['photo'])
def photo(message):
    bot.reply_to(message, "Foto diterima, sedang diproses AI...")

bot.polling()
