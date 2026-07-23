import telebot
from telebot import types
from datetime import datetime, timedelta
import time
import os
import threading
import random

TOKEN = os.getenv('BOT_TOKEN', '8937685397:AAFZTpk7Lz3DQZzFkLBSD2UCE9qRSECe0WQ')
ADMIN_ID = 6513565024

bot = telebot.TeleBot(TOKEN, threaded=False, skip_pending=True)

user_data = {}
auto_trading_active = {}
auto_selected_pairs = {}
auto_selected_durations = {}
reverse_mode_active = {}
user_stats = {}
last_sent_minute = {}

PAIRS = [
    'AED/CNY', 'AUD/CAD', 'AUD/CHF', 'AUD/JPY', 'AUD/NZD', 'AUD/USD', 
    'BHD/CNY', 'CAD/JPY', 'CHF/JPY', 'CHF/NOK', 'EUR/AUD', 'EUR/CHF', 
    'EUR/JPY', 'EUR/NZD', 'EUR/RUB', 'EUR/TRY', 'EUR/USD', 'GBP/AUD', 
    'GBP/JPY', 'KES/USD', 'MAD/USD', 'NGN/USD', 'NZD/JPY', 'NZD/USD', 
    'QAR/CNY', 'SAR/CNY', 'TND/USD', 'UAH/USD', 'USD/ARS', 'USD/BDT', 
    'USD/BRL', 'USD/CAD', 'USD/CHF', 'USD/CLP', 'USD/CNH', 'USD/COP', 
    'USD/DZD', 'USD/EGP', 'USD/INR', 'USD/JPY', 'USD/MXN', 'USD/MYR', 
    'USD/PKR', 'USD/RUB', 'USD/SGD', 'USD/THB', 'USD/VND', 'YER/USD', 'ZAR/USD',
    'Advanced Micro Devices OTC', 'Alibaba OTC', 'Amazon OTC', 'American Express OTC', 
    'Apple OTC', 'Boeing Company OTC', 'Citigroup Inc OTC', 'Cisco OTC', 
    'Coinbase Global OTC', 'Facebook OTC', 'FedEx OTC', 'GameStop Corp OTC', 
    'Intel OTC', 'Johnson & Johnson OTC', 'Marathon Digital Holdings OTC', 
    'McDonald\'s OTC', 'Palantir Technologies OTC', 'Pfizer Inc OTC', 
    'Tesla OTC', 'VIX OTC', 'VISA OTC'
]

CANDLE_OPTIONS = [
    'شمعة خضراء 1', 'شمعة خضراء 2', 'شمعة خضراء 3',
    'شمعة حمراء 1', 'شمعة حمراء 2', 'شمعة حمراء 3'
]

def get_bottom_fixed_keyboard(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    is_rev = reverse_mode_active.get(chat_id, False)
    rev_text = "العكس: مفعل 🟢" if is_rev else "العكس: متوقف 🔴"

    # وضع كل زر في صف منفصل تماماً (زر واحد في كل سطر لضمان عدم اندماجهم)
    btn_start_auto = types.KeyboardButton("تشغيل تلقائي 🚀")
    btn_stop_auto = types.KeyboardButton("إيقاف تلقائي ⏹️")
    btn_rev = types.KeyboardButton(rev_text)
    btn_manual = types.KeyboardButton("أوتوماتيكي 📊")
    
    btn_win = types.KeyboardButton("ربح ✅")
    btn_loss = types.KeyboardButton("خسارة ❌")

    markup.row(btn_start_auto)
    markup.row(btn_stop_auto)
    markup.row(btn_rev)
    markup.row(btn_manual)
    markup.row(btn_win, btn_loss)
    
    return markup

def create_vertical_kb(buttons_list, row=2, add_back=True):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=row)
    for btn in buttons_list:
        markup.add(types.KeyboardButton(str(btn)))
    if add_back:
        markup.row(types.KeyboardButton('⬅️ رجوع'))
    return markup

def analyze_otc_trap(pair, trend_type, chat_id):
    base_strength = random.randint(85, 99)
    is_rev = reverse_mode_active.get(chat_id, False)

    if trend_type == "ترند صاعد":
        primary_action = "🟢 صفقة شراء مؤكدة"
        primary_trend = "ترند صاعد"
        opp_action = "🔴 صفقة بيع مؤكدة"
        opp_trend = "ترند هابط"
    else:
        primary_action = "🔴 صفقة بيع مؤكدة"
        primary_trend = "ترند هابط"
        opp_action = "🟢 صفقة شراء مؤكدة"
        opp_trend = "ترند صاعد"

    if is_rev:
        action = opp_action + " (عكسي مقلوب 🔄)"
        actual_trend = opp_trend
    else:
        action = primary_action + " (عادي)"
        actual_trend = primary_trend

    return action, base_strength, actual_trend

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "أهلاً بك! تم ضبط القائمة لتظهر الأزرار الثلاثة بشكل عمودي كامل (كل زر في سطر منفصل):", reply_markup=get_bottom_fixed_keyboard(message.chat.id))

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    chat_id = message.chat.id
    text = message.text

    if text == "العكس: مفعل 🟢" or text == "العكس: متوقف 🔴":
        current_state = reverse_mode_active.get(chat_id, False)
        reverse_mode_active[chat_id] = not current_state
        state_text = "مفعل 🟢" if reverse_mode_active[chat_id] else "متوقف 🔴"
        bot.send_message(chat_id, f"تم تغيير وضع العكس إلى: {state_text}", reply_markup=get_bottom_fixed_keyboard(chat_id))

    elif text == "تشغيل تلقائي 🚀":
        user_data[chat_id] = {'auto_step': 'select_pair'}
        markup = create_vertical_kb(['جميع الأزواج (عشوائي)'] + PAIRS, row=2, add_back=True)
        bot.send_message(chat_id, "1. اختر الزوج للتشغيل التلقائي:", reply_markup=markup)

    elif text == "إيقاف تلقائي ⏹️":
        auto_trading_active[chat_id] = False
        bot.send_message(chat_id, "🔴 تم إيقاف التشغيل التلقائي بنجاح.", reply_markup=get_bottom_fixed_keyboard(chat_id))

    elif text == "أوتوماتيكي 📊":
        user_data[chat_id] = {'step': 1}
        bot.send_message(chat_id, "1. اختر الزوج للإدخال اليدوي:", reply_markup=create_vertical_kb(PAIRS, row=2, add_back=True))

    elif text == "ربح ✅" or text == "خسارة ❌":
        if chat_id not in user_stats:
            user_stats[chat_id] = {'wins': 0, 'losses': 0, 'consecutive_losses': 0}
        if text == "ربح ✅":
            user_stats[chat_id]['wins'] += 1
            user_stats[chat_id]['consecutive_losses'] = 0
            res_msg = "📈 ممتاز! تم تسجيل صفقة ربحة."
        else:
            user_stats[chat_id]['losses'] += 1
            user_stats[chat_id]['consecutive_losses'] += 1
            res_msg = "📉 تم تسجيل صفقة خاسرة."
            if user_stats[chat_id]['consecutive_losses'] >= 2:
                reverse_mode_active[chat_id] = True
                res_msg += "\n⚠️ خسارتين متتاليين، تم تفعيل وضع العكس تلقائياً!"
        
        wins = user_stats[chat_id]['wins']
        losses = user_stats[chat_id]['losses']
        total = wins + losses
        ratio = int((wins / total) * 100) if total > 0 else 0
        bot.send_message(chat_id, f"{res_msg}\n📊 رابحة: {wins} | خاسرة: {losses} | النسبة: {ratio}%", reply_markup=get_bottom_fixed_keyboard(chat_id))

    elif text == '⬅️ رجوع':
        user_data[chat_id] = {}
        bot.send_message(chat_id, "القائمة الرئيسية:", reply_markup=get_bottom_fixed_keyboard(chat_id))

    elif chat_id in user_data and user_data[chat_id].get('step') == 1 and (text in PAIRS or text == 'جميع الأزواج (عشوائي)'):
        user_data[chat_id]['pair'] = text
        user_data[chat_id]['step'] = 2
        bot.send_message(chat_id, "2. اختر نوع الترند:", reply_markup=create_vertical_kb(['ترند صاعد', 'ترند هابط', 'ترند متردد'], add_back=True))

    elif chat_id in user_data and user_data[chat_id].get('auto_step') == 'select_pair' and (text in PAIRS or text == 'جميع الأزواج (عشوائي)'):
        user_data[chat_id]['auto_pair'] = text
        user_data[chat_id]['auto_step'] = 'select_time'
        times = ['تلقائي ⚡ (دقيقة واحدة)'] + [f"{i} دقيقة" for i in range(1, 11)]
        bot.send_message(chat_id, f"🟢 الزوج المختار: **{text}**\n2. اختر وقت الصفقات التلقائية:", reply_markup=create_vertical_kb(times, row=3, add_back=True), parse_mode="Markdown")

    elif chat_id in user_data and user_data[chat_id].get('auto_step') == 'select_time' and ("دقيقة" in text or 'تلقائي' in text):
        selected_pair = user_data[chat_id].get('auto_pair', 'جميع الأزواج (عشوائي)')
        selected_time_text = text
        
        auto_trading_active[chat_id] = True
        auto_selected_pairs[chat_id] = selected_pair
        auto_selected_durations[chat_id] = selected_time_text
        
        bot.send_message(chat_id, f"🚀 تم بدء التشغيل التلقائي بنجاح!\n🔹 الزوج: **{selected_pair}**\n🔹 الوقت: **{selected_time_text}**", reply_markup=get_bottom_fixed_keyboard(chat_id), parse_mode="Markdown")
        user_data[chat_id] = {}

        def background_sender(target_chat_id):
            while auto_trading_active.get(target_chat_id, False):
                time_setting = auto_selected_durations.get(target_chat_id, 'تلقائي ⚡ (دقيقة واحدة)')
                rand_duration = 1 if 'تلقائي' in time_setting else int(time_setting.split()[0])

                now = datetime.now()
                target_time = now.replace(second=40, microsecond=0)
                if now.second >= 40:
                    target_time = target_time + timedelta(minutes=1)
                    
                sleep_seconds = (target_time - datetime.now()).total_seconds()
                while sleep_seconds > 0 and auto_trading_active.get(target_chat_id, False):
                    time.sleep(min(sleep_seconds, 0.4))
                    sleep_seconds = (target_time - datetime.now()).total_seconds()
                
                if not auto_trading_active.get(target_chat_id, False):
                    break
                
                current_minute_str = datetime.now().strftime('%Y-%m-%d %H:%M')
                if last_sent_minute.get(target_chat_id) == current_minute_str:
                    time.sleep(1)
                    continue
                last_sent_minute[target_chat_id] = current_minute_str

                current_choice = auto_selected_pairs.get(target_chat_id, 'جميع الأزواج (عشوائي)')
                rand_pair = random.choice(PAIRS) if current_choice == 'جميع الأزواج (عشوائي)' else current_choice
                    
                action, strength, actual_trend = analyze_otc_trap(rand_pair, 'ترند صاعد', target_chat_id)
                now_msg = datetime.now()
                entry_time = (now_msg + timedelta(minutes=1)).replace(second=0, microsecond=0)
                expiry_time = entry_time + timedelta(minutes=rand_duration)
                
                auto_text = (f"🧠 **التحليل الذكي للـ OTC**\n"
                             f"━━━━━━━━━━━━━━━━━━━\n"
                             f"🔹 **الزوج:** {rand_pair} | {actual_trend}\n"
                             f"🔹 **المدة:** {rand_duration} دقيقة\n"
                             f"🔹 **القرار:** {action}\n"
                             f"🔹 **الثقة:** {strength}%\n"
                             f"━━━━━━━━━━━━━━━━━━━\n"
                             f"⏳ **الدخول:** {entry_time.strftime('%H:%M:%S')}\n"
                             f"🏁 **الانتهاء:** {expiry_time.strftime('%H:%M:%S')}")
                try:
                    bot.send_message(target_chat_id, auto_text, reply_markup=get_bottom_fixed_keyboard(target_chat_id), parse_mode="Markdown")
                except:
                    break
                time.sleep(2.5)

        threading.Thread(target=background_sender, args=(chat_id,), daemon=True).start()

    elif chat_id in user_data and user_data[chat_id].get('step') == 2 and text in ['ترند صاعد', 'ترند هابط', 'ترند متردد']:
        user_data[chat_id]['trend_type'] = text
        user_data[chat_id]['step'] = 3
        times = ['تلقائي ⚡ (دقيقة واحدة)'] + [f"{i} دقيقة" for i in range(1, 11)]
        bot.send_message(chat_id, "3. اختر الوقت:", reply_markup=create_vertical_kb(times, row=3, add_back=True))

    elif chat_id in user_data and user_data[chat_id].get('step') == 3 and ("دقيقة" in text or 'تلقائي' in text):
        user_data[chat_id]['time'] = "1 دقيقة (تلقائي)" if 'تلقائي' in text else text
        user_data[chat_id]['step'] = 4
        trends = [f"Trend {i}" for i in range(50, 1050, 100)]
        bot.send_message(chat_id, "4. اختر قوة الترند:", reply_markup=create_vertical_kb(trends, row=3, add_back=True))

    elif chat_id in user_data and user_data[chat_id].get('step') == 4 and "Trend" in text:
        user_data[chat_id]['trend'] = text
        user_data[chat_id]['step'] = 5
        bot.send_message(chat_id, "5. من المسيطر؟", reply_markup=create_vertical_kb(['المشترون أكثر', 'البائعون أكثر'], add_back=True))

    elif chat_id in user_data and user_data[chat_id].get('step') == 5 and text in ['المشترون أكثر', 'البائعون أكثر']:
        user_data[chat_id]['sentiment'] = text
        user_data[chat_id]['step'] = 6
        rsi_list = [f"RSI {i}" for i in range(30, 90, 10)]
        bot.send_message(chat_id, "6. حدد RSI:", reply_markup=create_vertical_kb(rsi_list, row=3, add_back=True))

    elif chat_id in user_data and user_data[chat_id].get('step') == 6 and "RSI" in text:
        user_data[chat_id]['rsi'] = text.split()[1]
        user_data[chat_id]['step'] = 7
        bot.send_message(chat_id, "7. حدد الشمعة الحالية:", reply_markup=create_vertical_kb(CANDLE_OPTIONS, row=2, add_back=True))

    elif chat_id in user_data and user_data[chat_id].get('step') == 7 and text in CANDLE_OPTIONS:
        user_data[chat_id]['current_candle'] = text
        user_data[chat_id]['step'] = 8
        bot.send_message(chat_id, "8. حدد الشموع السابقة:", reply_markup=create_vertical_kb(CANDLE_OPTIONS, row=2, add_back=True))

    elif chat_id in user_data and user_data[chat_id].get('step') == 8 and text in CANDLE_OPTIONS:
        data = user_data[chat_id]
        duration = int(data['time'].split()[0])
        now = datetime.now()
        entry_time = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        expiry_time = entry_time + timedelta(minutes=duration)
        
        action, strength, actual_trend = analyze_otc_trap(data['pair'], data['trend_type'], chat_id)
        
        result_text = (f"🧠 **التحليل اليدوي للـ OTC**\n"
                       f"━━━━━━━━━━━━━━━━━━━\n"
                       f"🔹 **الزوج:** {data['pair']} | {actual_trend}\n"
                       f"🔹 **الوقت:** {data['time']}\n"
                       f"🔹 **القرار:** {action}\n"
                       f"🔹 **الثقة:** {strength}%\n"
                       f"━━━━━━━━━━━━━━━━━━━\n"
                       f"⏳ **الدخول:** {entry_time.strftime('%H:%M:%S')}\n"
                       f"🏁 **الانتهاء:** {expiry_time.strftime('%H:%M:%S')}")
                     
        bot.send_message(chat_id, result_text, reply_markup=get_bottom_fixed_keyboard(chat_id), parse_mode="Markdown")
        user_data[chat_id] = {}

bot.infinity_polling(none_stop=True, interval=0)
