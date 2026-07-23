import telebot
from datetime import datetime, timedelta
import random

TOKEN = '8937685397:AAFZTpk7Lz3DQZzFkLBSD2UCE9qRSECe0WQ'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('إشارات التداول')
    btn2 = telebot.types.KeyboardButton('Classic mode')
    btn3 = telebot.types.KeyboardButton('التداولات')
    btn4 = telebot.types.KeyboardButton('التداول الاجتماعي')
    btn5 = telebot.types.KeyboardButton('المزيد')
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5)
    
    bot.reply_to(message, "أهلاً بك! اختر أحد الأوضاع أو الخيارات أدناه:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('إشارات التداول')
    btn2 = telebot.types.KeyboardButton('Classic mode')
    btn3 = telebot.types.KeyboardButton('التداولات')
    btn4 = telebot.types.KeyboardButton('التداول الاجتماعي')
    btn5 = telebot.types.KeyboardButton('المزيد')
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5)

    if message.text in ['إشارات التداول', 'Classic mode']:
        now = datetime.now() + timedelta(hours=3)
        entry_time = now + timedelta(minutes=1)
        duration_minutes = 3
        expiry_time = entry_time + timedelta(minutes=duration_minutes)
        strength = random.randint(85, 99)
        
        response_text = (
            "📊 **تقرير الصفقة الجديد**\n\n"
            f"💪 **قوة الصفقة:** {strength}%\n"
            f"⏳ **توقيت الدخول:** {entry_time.strftime('%H:%M:%S')}\n"
            f"⏱️ **توقيت الانتهاء:** {expiry_time.strftime('%H:%M:%S')}\n"
            f"⌛ **مدة الصفقة:** {duration_minutes} دقائق\n\n"
            "✨ بالتوفيق إن شاء الله!"
        )
        bot.reply_to(message, response_text, parse_mode="Markdown", reply_markup=markup)
        
    elif message.text == 'التداولات':
        bot.reply_to(message, "📂 سجل التداولات النشطة حالياً.", reply_markup=markup)
        
    elif message.text == 'التداول الاجتماعي':
        bot.reply_to(message, "👥 قسم التداول الاجتماعي لمتابعة الإشارات الجماعية.", reply_markup=markup)
        
    elif message.text == 'المزيد':
        bot.reply_to(message, "⚙️ خيارات إضافية وإعدادات البوت.", reply_markup=markup)
        
    else:
        bot.reply_to(message, "الرجاء استخدام الأزرار في الأسفل للتنقل.", reply_markup=markup)

bot.infinity_polling()
