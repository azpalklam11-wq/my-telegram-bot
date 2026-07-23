import telebot
from datetime import datetime, timedelta
import random

TOKEN = '8937685397:AAFZTpk7Lz3DQZzFkLBSD2UCE9qRSECe0WQ'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_btn = telebot.types.KeyboardButton('زر البدء')
    markup.add(start_btn)
    bot.reply_to(message, "أهلاً بك في بوت التداول الذكي. اضغط على زر البدء أدناه لإصدار إشارة التداول.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == 'زر البدء':
        # حساب وقت الدخول (بعد دقيقة واحدة من الآن)
        now = datetime.now() + timedelta(hours=3) # تعديل التوقيت حسب النطاق الزمني إن لزم
        entry_time = now + timedelta(minutes=1)
        
        # مدة الصفقة (مثلاً 3 دقائق) والانتهاء
        duration_minutes = 3
        expiry_time = entry_time + timedelta(minutes=3)
        
        # قوة الصفقة عشوائية بين 85% و 99%
        strength = random.randint(85, 99)
        
        response_text = (
            "📊 **تقرير الصفقة الجديد**\n\n"
            f"💪 **قوة الصفقة:** {strength}%\n"
            f"⏳ **توقيت الدخول:** {entry_time.strftime('%H:%M:%S')}\n"
            f"⏱️ **توقيت الانتهاء:** {expiry_time.strftime('%H:%M:%S')}\n"
            f"⌛ **مدة الصفقة:** {duration_minutes} دقائق\n\n"
            "✨ بالتوفيق إن شاء الله!"
        )
        
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_btn = telebot.types.KeyboardButton('زر البدء')
        markup.add(start_btn)
        
        bot.reply_to(message, response_text, parse_mode="Markdown", reply_markup=markup)
    else:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_btn = telebot.types.KeyboardButton('زر البدء')
        markup.add(start_btn)
        bot.reply_to(message, "الرجاء استخدام زر البدء للحصول على إشارات التداول.", reply_markup=markup)

bot.infinity_polling()
