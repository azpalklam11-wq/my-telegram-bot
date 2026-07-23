import telebot

TOKEN = '8937685397:AAFZTpk7Lz3DQZzFkLBSD2UCE9qRSECe0WQ'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_btn = telebot.types.KeyboardButton('زر البدء')
    markup.add(start_btn)
    bot.reply_to(message, "أهلاً بك! تم تشغيل البوت بنجاح على المنصة.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text == 'زر البدء':
        bot.reply_to(message, "تم تفعيل زر البدء بنجاح، قوة الصفقة: 95%، التوقيت: دقيقة واحدة.")
    else:
        bot.reply_to(message, "أرسل /start لبدء التشغيل.")

bot.infinity_polling()
