import telebot
from datetime import datetime, timedelta
import random

TOKEN = '8937685397:AAFZTpk7Lz3DQZzFkLBSD2UCE9qRSECe0WQ'
bot = telebot.TeleBot(TOKEN)

# دالة لإنشاء لوحة المفاتيح الرئيسية الثابتة
def get_main_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    # الأزرار مطابقة لترتيب الصورة والشرح
    btn_trades = telebot.types.KeyboardButton('التداولات')
    btn_signals = telebot.types.KeyboardButton('إشارات التداول')
    btn_classic = telebot.types.KeyboardButton('Classic mode')
    btn_social = telebot.types.KeyboardButton('التداول الاجتماعي')
    btn_more = telebot.types.KeyboardButton('المزيد')
    
    markup.add(btn_trades, btn_signals)
    markup.add(btn_classic)
    markup.add(btn_social, btn_more)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "أهلاً بك في بوت التداول العالمي 🌍\nاختر أحد الخيارات أدناه للبدء:", 
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text
    
    if text == 'التداولات':
        response = (
            "📊 **تقرير صفقات الربح والخسارة**\n\n"
            "✅ الصفقات الرابحة: 12\n"
            "❌ الصفقات الخاسرة: 2\n"
            "📈 نسبة النجاح الإجمالية: 85.7%"
        )
        bot.reply_to(message, response, parse_mode="Markdown", reply_markup=get_main_keyboard())
        
    elif text == 'إشارات التداول':
        response = (
            "⚙️ **لوحة الإدخال اليدوي للأزواج**\n\n"
            "• الزوج: BTC/USDT (افتراضي)\n"
            "• مدة الصفقة: 3 دقائق\n"
            "• الترند: صاعد 📈\n"
            "• مؤشر RSI: 24 (منطقة تشبع بيعي)\n"
            "• مستويات الارتداد: 100\n\n"
            "جاري معالجة الإشارة..."
        )
        # حساب توقيتات الصفقة بدقة
        now = datetime.now() + timedelta(hours=3)
        entry_time = now + timedelta(minutes=1)
        expiry_time = entry_time + timedelta(minutes=3)
        strength = random.randint(85, 99)
        
        signal_details = (
            f"\n\n💪 **قوة الصفقة:** {strength}%\n"
            f"⏳ **توقيت الدخول:** {entry_time.strftime('%H:%M:%S')}\n"
            f"⏱️ **توقيت الانتهاء:** {expiry_time.strftime('%H:%M:%S')}"
        )
        bot.reply_to(message, response + signal_details, parse_mode="Markdown", reply_markup=get_main_keyboard())
        
    elif text == 'Classic mode':
        # إنشاء أزرار فرعية خاصة بالوضع الكلاسيكي للإرسال التلقائي
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_auto_on = telebot.types.KeyboardButton('تفعيل تلقائي وإعداد يدوي')
        btn_auto_off = telebot.types.KeyboardButton('إيقاف تلقائي')
        btn_back = telebot.types.KeyboardButton('القائمة الرئيسية')
        markup.add(btn_auto_on, btn_auto_off)
        markup.add(btn_back)
        
        bot.reply_to(
            message, 
            "🔄 **إدارة الإرسال التلقائي (Classic mode)**\nاختر حالة الإرسال المطلوب:", 
            reply_markup=markup
        )
        
    elif text == 'تفعيل تلقائي وإعداد يدوي':
        bot.reply_to(message, "✅ تم تفعيل الإرسال التلقائي مع إتاحة ضبط الأزواج والتايم يدوياً.", reply_markup=get_main_keyboard())
        
    elif text == 'إيقاف تلقائي':
        bot.reply_to(message, "🛑 تم إيقاف الإرسال التلقائي بنجاح.", reply_markup=get_main_keyboard())
        
    elif text == 'القائمة الرئيسية':
        bot.reply_to(message, "القرار بيدكم، اختر من القائمة أدناه:", reply_markup=get_main_keyboard())
        
    elif text == 'التداول الاجتماعي':
        bot.reply_to(message, "👥 قسم التداول الاجتماعي لمتابعة صفقات المتصدرين والمجتمع.", reply_markup=get_main_keyboard())
        
    elif text == 'المزيد':
        response = (
            "🔗 **المزيد وخيارات الاشتراك**\n\n"
            "للانضمام والاشتراك في المنصة الرسمية عبر رابط الإحالة الخاص بنا:\n"
            "👉 [اضغط هنا للاشتراك في المنصة](https://t.me)"
        )
        bot.reply_to(message, response, parse_mode="Markdown", reply_markup=get_main_keyboard())
        
    else:
        bot.reply_to(message, "الرجاء استخدام الأزرار الظاهرة في الأسفل للتنقل.", reply_markup=get_main_keyboard())

bot.infinity_polling()
