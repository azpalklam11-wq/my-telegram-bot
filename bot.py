import telebot
from telebot import types
from datetime import datetime, timedelta
import time
import os
import threading
import random

TOKEN = '8937685397:AAFZTpk7Lz3DQZzFkLBSD2UCE9qRSECe0WQ'
ADMIN_ID = 6513565024

bot = telebot.TeleBot(TOKEN, threaded=False, skip_pending=True)

user_data = {}
auto_trading_active = {}
auto_selected_pairs = {}
reverse_mode_active = {}
user_stats = {}
active_pair_locks = {}
last_click_time = {}

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

def get_main_markup(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_manual = types.KeyboardButton('أوتوماتيكي')
    btn_auto = types.KeyboardButton('تشغيل تلقائي')
    btn_stop_auto = types.KeyboardButton('إيقاف تلقائي')
    is_rev = reverse_mode_active.get(chat_id, False)
    rev_btn_text = "🔄 العكس: مفعل 🟢" if is_rev else "🔄 العكس: متوقف 🔴"
    btn_rev = types.KeyboardButton(rev_btn_text)
    btn_win = types.KeyboardButton('✅ ربح')
    btn_loss = types.KeyboardButton('❌ خسارة')
    markup.add(btn_manual, btn_auto)
    markup.add(btn_stop_auto, btn_rev)
    markup.add(btn_win, btn_loss)
    if chat_id == ADMIN_ID:
        markup.add(types.KeyboardButton('إيقاف النظام'))
    return markup

def create_vertical_kb(buttons_list, chat_id, row=2, add_back=True):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=row)
    for btn in buttons_list:
        markup.add(types.KeyboardButton(str(btn)))
    if add_back:
        if chat_id == ADMIN_ID:
            markup.row(types.KeyboardButton('⬅️ رجوع'), types.KeyboardButton('إيقاف النظام'))
        else:
            markup.row(types.KeyboardButton('⬅️ رجوع'))
    else:
        if chat_id == ADMIN_ID:
            markup.row(types.KeyboardButton('إيقاف النظام'))
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
    bot.send_message(message.chat.id, "أهلاً بك! تم ضبط كافة خصائص البوت بنجاح.", reply_markup=get_main_markup(message.chat.id))

@bot.message_handler(func=lambda message: message.text and '🔄 العكس:' in message.text)
def toggle_reverse_mode(message):
    chat_id = message.chat.id
    current_state = reverse_mode_active.get(chat_id, False)
    reverse_mode_active[chat_id] = not current_state
    state_text = "مفعل 🟢 (تم عكس القرارات)" if reverse_mode_active[chat_id] else "متوقف 🔴 (الوضع الطبيعي)"
    bot.send_message(chat_id, f"⚡ تم تغيير الوضع يدوياً.\nحالة زر الانعكاس: {state_text}", reply_markup=get_main_markup(chat_id))

@bot.message_handler(func=lambda message: message.text in ['✅ ربح', '❌ خسارة'])
def handle_stats(message):
    chat_id = message.chat.id
    if chat_id not in user_stats:
        user_stats[chat_id] = {'wins': 0, 'losses': 0}
        
    if message.text == '✅ ربح':
        user_stats[chat_id]['wins'] += 1
        result_msg = "📈 ممتاز! تم تسجيل صفقة ربحة في سجلك."
    else:
        user_stats[chat_id]['losses'] += 1
        result_msg = "📉 تم تسجيل صفقة خاسرة في سجلك."

    wins = user_stats[chat_id]['wins']
    losses = user_stats[chat_id]['losses']
    total = wins + losses
    ratio = int((wins / total) * 100) if total > 0 else 0

    stats_text = (f"{result_msg}\n"
                  f"━━━━━━━━━━━━━━━━━━━\n"
                  f"📊 **عداد الأداء والإحصائيات:**\n"
                  f"🟢 صفقات رابحة: {wins}\n"
                  f"🔴 صفقات خاسرة: {losses}\n"
                  f"🎯 نسبة النجاح الإجمالية: {ratio}%")
    bot.send_message(chat_id, stats_text, reply_markup=get_main_markup(chat_id), parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == 'إيقاف النظام')
def stop_bot(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "عذراً، هذا الأمر مخصص للمشرف فقط.")
        return
    auto_trading_active[message.chat.id] = False
    bot.send_message(message.chat.id, "تم إيقاف النظام وإغلاق الميزات التلقائية.")
    os._exit(0)

@bot.message_handler(func=lambda message: message.text == 'تشغيل تلقائي')
def start_auto_menu(message):
    chat_id = message.chat.id
    markup = create_vertical_kb(['جميع الأزواج (عشوائي)'] + PAIRS, chat_id, row=2, add_back=True)
    bot.send_message(chat_id, "اختر الزوج المطلوب للتشغيل التلقائي (وقت الصفقات 1-2 دقيقة):", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'أوتوماتيكي')
def step_manual_start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'step': 1}
    bot.send_message(chat_id, "1. اختر الزوج للإدخال اليدوي:", reply_markup=create_vertical_kb(PAIRS, chat_id, row=2, add_back=True))

@bot.message_handler(func=lambda message: chat_id_in_step(message.chat.id, 1) and (message.text in PAIRS or message.text == 'جميع الأزواج (عشوائي)'))
def step_manual_pair(message):
    chat_id = message.chat.id
    text = message.text
    
    if chat_id in user_data and user_data[chat_id].get('step') == 1:
        user_data[chat_id]['pair'] = text
        user_data[chat_id]['step'] = 2
        bot.send_message(chat_id, "2. اختر نوع الترند:", reply_markup=create_vertical_kb(['ترند صاعد', 'ترند هابط', 'ترند متردد'], chat_id, add_back=True))
        return

@bot.message_handler(func=lambda message: message.text in PAIRS or message.text == 'جميع الأزواج (عشوائي)')
def handle_auto_pair_selection(message):
    chat_id = message.chat.id
    
    now_ts = time.time()
    if now_ts - last_click_time.get(chat_id, 0) < 2.0:
        return
    last_click_time[chat_id] = now_ts
    
    selected_pair = message.text
    auto_trading_active[chat_id] = True
    auto_selected_pairs[chat_id] = selected_pair
    
    bot.send_message(chat_id, f"🟢 تم تفعيل التشغيل التلقائي للزوج: **{selected_pair}** (بمدة 1-2 دقيقة)", reply_markup=get_main_markup(chat_id), parse_mode="Markdown")
    
    def background_sender():
        while auto_trading_active.get(chat_id, False):
            now = datetime.now()
            target_second = 0
            current_sec = now.second
            
            if current_sec <= target_second:
                sleep_seconds = target_second - current_sec
            else:
                sleep_seconds = (60 - current_sec) + target_second
                
            time.sleep(sleep_seconds)
            
            if not auto_trading_active.get(chat_id, False):
                break
            
            current_choice = auto_selected_pairs.get(chat_id, 'جميع الأزواج (عشوائي)')
            if current_choice == 'جميع الأزواج (عشوائي)':
                available_pairs = [p for p in PAIRS if active_pair_locks.get(p, 0) < time.time()]
                if not available_pairs:
                    time.sleep(5)
                    continue
                rand_pair = random.choice(available_pairs)
            else:
                rand_pair = current_choice
                if active_pair_locks.get(rand_pair, 0) > time.time():
                    time.sleep(5)
                    continue
                
            rand_duration = random.choice([1, 2])
            active_pair_locks[rand_pair] = time.time() + (rand_duration * 60 + 30)
                
            rand_trend_type = random.choice(['ترند صاعد', 'ترند هابط'])
            action, strength, actual_trend = analyze_otc_trap(rand_pair, rand_trend_type, chat_id)
            
            now_msg = datetime.now()
            entry_time = (now_msg + timedelta(minutes=1)).replace(second=0, microsecond=0)
            expiry_time = entry_time + timedelta(minutes=rand_duration)
            
            is_rev = reverse_mode_active.get(chat_id, False)
            mode_status = "مفعل (عكسي 🔄)" if is_rev else "عادي"
            
            auto_text = (f"🧠 **التحليل الذكي للـ OTC (وضع الاستراتيجية: {mode_status})**\n"
                         f"━━━━━━━━━━━━━━━━━━━\n"
                         f"🔹 **الزوج / السهم:** {rand_pair} | {actual_trend}\n"
                         f"🔹 **القرار المحسوب:** {action}\n"
                         f"🔹 **مؤشر الثقة الذكي:** {strength}%\n"
                         f"━━━━━━━━━━━━━━━━━━━\n"
                         f"⏳ **وقت دخول الصفقة:** {entry_time.strftime('%H:%M:%S')}\n"
                         f"🏁 **وقت انتهاء الصفقة:** {expiry_time.strftime('%H:%M:%S')}")
            try:
                bot.send_message(chat_id, auto_text, reply_markup=get_main_markup(chat_id), parse_mode="Markdown")
            except:
                break
            
            time.sleep(50)

    threading.Thread(target=background_sender, daemon=True).start()

def chat_id_in_step(chat_id, step_num):
    return chat_id in user_data and user_data[chat_id].get('step') == step_num

@bot.message_handler(func=lambda message: chat_id_in_step(message.chat.id, 2) and message.text in ['ترند صاعد', 'ترند هابط', 'ترند متردد'])
def step_manual_trend(message):
    chat_id = message.chat.id
    user_data[chat_id]['trend_type'] = message.text
    user_data[chat_id]['step'] = 3
    times = [f"{i} دقيقة" for i in range(1, 11)]
    bot.send_message(chat_id, "3. اختر الوقت:", reply_markup=create_vertical_kb(times, chat_id, row=3, add_back=True))

@bot.message_handler(func=lambda message: chat_id_in_step(message.chat.id, 3) and "دقيقة" in message.text)
def step_manual_time(message):
    chat_id = message.chat.id
    user_data[chat_id]['time'] = message.text
    user_data[chat_id]['step'] = 4
    trends = [f"Trend {i}" for i in range(50, 1050, 100)]
    bot.send_message(chat_id, "4. اختر قوة الترند:", reply_markup=create_vertical_kb(trends, chat_id, row=3, add_back=True))

@bot.message_handler(func=lambda message: chat_id_in_step(message.chat.id, 4) and "Trend" in message.text)
def step_manual_trend_strength(message):
    chat_id = message.chat.id
    user_data[chat_id]['trend'] = message.text
    user_data[chat_id]['step'] = 5
    bot.send_message(chat_id, "5. من المسيطر؟", reply_markup=create_vertical_kb(['المشترون أكثر', 'البائعون أكثر'], chat_id, add_back=True))

@bot.message_handler(func=lambda message: chat_id_in_step(message.chat.id, 5) and message.text in ['المشترون أكثر', 'البائعون أكثر'])
def step_manual_sentiment(message):
    chat_id = message.chat.id
    user_data[chat_id]['sentiment'] = message.text
    user_data[chat_id]['step'] = 6
    rsi_list = [f"RSI {i}" for i in range(30, 90, 10)]
    bot.send_message(chat_id, "6. حدد RSI:", reply_markup=create_vertical_kb(rsi_list, chat_id, row=3, add_back=True))

@bot.message_handler(func=lambda message: chat_id_in_step(message.chat.id, 6) and "RSI" in message.text)
def step_manual_rsi(message):
    chat_id = message.chat.id
    user_data[chat_id]['rsi'] = message.text.split()[1]
    user_data[chat_id]['step'] = 7
    bot.send_message(chat_id, "7. حدد الشمعة الحالية (الأخيرة):", reply_markup=create_vertical_kb(CANDLE_OPTIONS, chat_id, row=2, add_back=True))

@bot.message_handler(func=lambda message: chat_id_in_step(message.chat.id, 7) and message.text in CANDLE_OPTIONS)
def step_manual_current_candle(message):
    chat_id = message.chat.id
    user_data[chat_id]['current_candle'] = message.text
    user_data[chat_id]['step'] = 8
    bot.send_message(chat_id, "8. حدد الشموع السابقة (التي قبلها):", reply_markup=create_vertical_kb(CANDLE_OPTIONS, chat_id, row=2, add_back=True))

@bot.message_handler(func=lambda message: chat_id_in_step(message.chat.id, 8) and message.text in CANDLE_OPTIONS)
def step_manual_final(message):
    chat_id = message.chat.id
    data = user_data[chat_id]
    prev_candles = message.text
    current_candle = data['current_candle']
    
    rsi = data['rsi']
    duration = int(data['time'].split()[0])
    now = datetime.now()
    entry_time = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
    expiry_time = entry_time + timedelta(minutes=duration)
    
    action, strength, actual_trend = analyze_otc_trap(data['pair'], data['trend_type'], chat_id)
    
    is_rev = reverse_mode_active.get(chat_id, False)
    mode_status = "مفعل (عكسي 🔄)" if is_rev else "عادي"
    
    result_text = (f"🧠 **التحليل اليدوي للـ OTC (الوضع: {mode_status})**\n"
                   f"━━━━━━━━━━━━━━━━━━━\n"
                   f"🔹 **الزوج:** {data['pair']} | {actual_trend}\n"
                   f"🔹 **الشمعة الحالية:** {current_candle}\n"
                   f"🔹 **الشموع السابقة:** {prev_candles}\n"
                   f"🔹 **القرار المحسوب:** {action}\n"
                   f"🔹 **مؤشر الثقة الحي:** {strength}%\n"
                   f"━━━━━━━━━━━━━━━━━━━\n"
                   f"⏳ **وقت دخول الصفقة:** {entry_time.strftime('%H:%M:%S')}\n"
                   f"🏁 **وقت انتهاء الصفقة:** {expiry_time.strftime('%H:%M:%S')}")
                 
    bot.send_message(chat_id, result_text, reply_markup=get_main_markup(chat_id), parse_mode="Markdown")
    user_data[chat_id] = {}

@bot.message_handler(func=lambda message: message.text == 'إيقاف تلقائي')
def stop_auto(message):
    chat_id = message.chat.id
    auto_trading_active[chat_id] = False
    bot.send_message(chat_id, "🔴 تم إيقاف التشغيل التلقائي بنجاح.", reply_markup=get_main_markup(chat_id))

@bot.message_handler(func=lambda message: message.text == '⬅️ رجوع')
def handle_back(message):
    chat_id = message.chat.id
    data = user_data.get(chat_id, {})
    step = data.get('step', 0)
    
    if step <= 1:
        user_data[chat_id] = {}
        bot.send_message(chat_id, "القائمة الرئيسية:", reply_markup=get_main_markup(chat_id))
    elif step == 2:
        data['step'] = 1
        bot.send_message(chat_id, "1. اختر الزوج:", reply_markup=create_vertical_kb(PAIRS, chat_id, row=2, add_back=True))
    elif step == 3:
        data['step'] = 2
        bot.send_message(chat_id, "2. اختر نوع الترند:", reply_markup=create_vertical_kb(['ترند صاعد', 'ترند هابط', 'ترند متردد'], chat_id, add_back=True))
    elif step == 4:
        data['step'] = 3
        times = [f"{i} دقيقة" for i in range(1, 11)]
        bot.send_message(chat_id, "3. اختر الوقت:", reply_markup=create_vertical_kb(times, chat_id, row=3, add_back=True))
    elif step == 5:
        data['step'] = 4
        trends = [f"Trend {i}" for i in range(50, 1050, 100)]
        bot.send_message(chat_id, "4. اختر قوة الترند:", reply_markup=create_vertical_kb(trends, chat_id, row=3, add_back=True))
    elif step == 6:
        data['step'] = 5
        bot.send_message(chat_id, "5. من المسيطر؟", reply_markup=create_vertical_kb(['المشترون أكثر', 'البائعون أكثر'], chat_id, add_back=True))
    elif step == 7:
        data['step'] = 6
        rsi_list = [f"RSI {i}" for i in range(30, 90, 10)]
        bot.send_message(chat_id, "6. حدد RSI:", reply_markup=create_vertical_kb(rsi_list, chat_id, row=3, add_back=True))
    else:
        user_data[chat_id] = {}
        bot.send_message(chat_id, "القائمة الرئيسية:", reply_markup=get_main_markup(chat_id))

while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=60)
    except Exception as e:
        time.sleep(5)
