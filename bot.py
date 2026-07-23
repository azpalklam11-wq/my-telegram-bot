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
auto_selected_durations = {}
reverse_mode_active = {}
user_stats = {}
active_pair_locks = {}
last_click_time = {}
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

def get_inline_markup(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=5)
    is_rev = reverse_mode_active.get(chat_id, False)
    rev_text = "🔄 العكس: مفعل" if is_rev else "🔄 العكس: متوقف"
    
    # الأزرار في شريط أفقي واحد تماماً مثل الصورة المطلوبة
    btn_auto = types.InlineKeyboardButton('تشغيل', callback_data='start_auto')
    btn_stop = types.InlineKeyboardButton('إيقاف', callback_data='stop_auto')
    btn_manual = types.InlineKeyboardButton('أوتوماتيكي', callback_data='manual_mode')
    btn_rev = types.InlineKeyboardButton(rev_text, callback_data='toggle_rev')
    btn_stats = types.InlineKeyboardButton('📊 الإحصائيات', callback_data='show_stats')
    
    markup.row(btn_auto, btn_stop, btn_manual, btn_rev, btn_stats)
    
    # شريط إضافي لزر ربح وخسارة تحتها مباشرة
    btn_win = types.InlineKeyboardButton('✅ ربح', callback_data='win_btn')
    btn_loss = types.InlineKeyboardButton('❌ خسارة', callback_data='loss_btn')
    markup.row(btn_win, btn_loss)
    return markup

def create_vertical_kb(buttons_list, chat_id, row=2, add_back=True):
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
    bot.send_message(message.chat.id, "أهلاً بك! إليك لوحة التحكم الأفقية:", reply_markup=get_inline_markup(message.chat.id))

@bot.callback_query_handler(func=lambda call: True)
def handle_inline_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data
    
    if data == 'toggle_rev':
        current_state = reverse_mode_active.get(chat_id, False)
        reverse_mode_active[chat_id] = not current_state
        state_text = "مفعل 🟢" if reverse_mode_active[chat_id] else "متوقف 🔴"
        bot.answer_callback_query(call.id, f"تم تغيير وضع العكس: {state_text}")
        try:
            bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=get_inline_markup(chat_id))
        except:
            pass

    elif data == 'show_stats':
        if chat_id not in user_stats:
            user_stats[chat_id] = {'wins': 0, 'losses': 0, 'consecutive_losses': 0}
        wins = user_stats[chat_id]['wins']
        losses = user_stats[chat_id]['losses']
        total = wins + losses
        ratio = int((wins / total) * 100) if total > 0 else 0
        stats_text = (f"📊 **لوحة الإحصائيات الحالية:**\n"
                      f"━━━━━━━━━━━━━━━━━━━\n"
                      f"🟢 صفقات رابحة: {wins}\n"
                      f"🔴 صفقات خاسرة: {losses}\n"
                      f"🎯 نسبة النجاح الإجمالية: {ratio}%")
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, stats_text, reply_markup=get_inline_markup(chat_id), parse_mode="Markdown")

    elif data == 'win_btn' or data == 'loss_btn':
        if chat_id not in user_stats:
            user_stats[chat_id] = {'wins': 0, 'losses': 0, 'consecutive_losses': 0}
        if data == 'win_btn':
            user_stats[chat_id]['wins'] += 1
            user_stats[chat_id]['consecutive_losses'] = 0
            res_msg = "📈 ممتاز! تم تسجيل صفقة ربحة."
        else:
            user_stats[chat_id]['losses'] += 1
            user_stats[chat_id]['consecutive_losses'] += 1
            res_msg = "📉 تم تسجيل صفقة خاسرة."
            if user_stats[chat_id]['consecutive_losses'] >= 2:
                reverse_mode_active[chat_id] = True
                res_msg += "\n⚠️ رصدنا خسارتين، تم تفعيل (🔄 وضع العكس أوتوماتيكياً)!"
        
        wins = user_stats[chat_id]['wins']
        losses = user_stats[chat_id]['losses']
        total = wins + losses
        ratio = int((wins / total) * 100) if total > 0 else 0
        bot.answer_callback_query(call.id, "تم تسجيل النتيجة بنجاح")
        bot.send_message(chat_id, f"{res_msg}\n📊 رابحة: {wins} | خاسرة: {losses} | النسبة: {ratio}%", reply_markup=get_inline_markup(chat_id))

    elif data == 'start_auto':
        bot.answer_callback_query(call.id)
        user_data[chat_id] = {'auto_step': 'select_pair'}
        markup = create_vertical_kb(['جميع الأزواج (عشوائي)'] + PAIRS, chat_id, row=2, add_back=True)
        bot.send_message(chat_id, "1. اختر الزوج للتشغيل التلقائي:", reply_markup=markup)

    elif data == 'stop_auto':
        auto_trading_active[chat_id] = False
        bot.answer_callback_query(call.id, "تم إيقاف التشغيل التلقائي")
        bot.send_message(chat_id, "🔴 تم إيقاف التشغيل التلقائي بنجاح.", reply_markup=get_inline_markup(chat_id))

    elif data == 'manual_mode':
        bot.answer_callback_query(call.id)
        user_data[chat_id] = {'step': 1}
        bot.send_message(chat_id, "1. اختر الزوج للإدخال اليدوي:", reply_markup=create_vertical_kb(PAIRS, chat_id, row=2, add_back=True))

@bot.message_handler(func=lambda message: chat_id_in_step(message.chat.id, 1) and (message.text in PAIRS or message.text == 'جميع الأزواج (عشوائي)'))
def step_manual_pair(message):
    chat_id = message.chat.id
    if chat_id in user_data and user_data[chat_id].get('step') == 1:
        user_data[chat_id]['pair'] = message.text
        user_data[chat_id]['step'] = 2
        bot.send_message(chat_id, "2. اختر نوع الترند:", reply_markup=create_vertical_kb(['ترند صاعد', 'ترند هابط', 'ترند متردد'], chat_id, add_back=True))

@bot.message_handler(func=lambda message: chat_id_in_auto_step(message.chat.id, 'select_pair') and (message.text in PAIRS or message.text == 'جميع الأزواج (عشوائي)'))
def handle_auto_pair_chosen(message):
    chat_id = message.chat.id
    user_data[chat_id]['auto_pair'] = message.text
    user_data[chat_id]['auto_step'] = 'select_time'
    times = ['تلقائي ⚡ (دقيقة واحدة)'] + [f"{i} دقيقة" for i in range(1, 11)]
    bot.send_message(chat_id, f"🟢 الزوج المختار: **{message.text}**\n2. اختر وقت الصفقات التلقائية:", reply_markup=create_vertical_kb(times, chat_id, row=3, add_back=True), parse_mode="Markdown")

@bot.message_handler(func=lambda message: chat_id_in_auto_step(message.chat.id, 'select_time') and ("دقيقة" in message.text or 'تلقائي' in message.text))
def handle_auto_time_chosen(message):
    chat_id = message.chat.id
    selected_pair = user_data[chat_id].get('auto_pair', 'جميع الأزواج (عشوائي)')
    selected_time_text = message.text
    
    auto_trading_active[chat_id] = False
    time.sleep(0.3)
    auto_trading_active[chat_id] = True
    auto_selected_pairs[chat_id] = selected_pair
    auto_selected_durations[chat_id] = selected_time_text
    
    bot.send_message(chat_id, f"🚀 تم بدء التشغيل التلقائي بنجاح!\n🔹 الزوج: **{selected_pair}**\n🔹 وقت الصفقة: **{selected_time_text}**", reply_markup=get_inline_markup(chat_id), parse_mode="Markdown")
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
                         f"🔹 **مؤشر الثقة:** {strength}%\n"
                         f"━━━━━━━━━━━━━━━━━━━\n"
                         f"⏳ **الدخول:** {entry_time.strftime('%H:%M:%S')}\n"
                         f"🏁 **الانتهاء:** {expiry_time.strftime('%H:%M:%S')}")
            try:
                bot.send_message(target_chat_id, auto_text, reply_markup=get_inline_markup(target_chat_id), parse_mode="Markdown")
            except:
                break
            time.sleep(2.5)

    threading.Thread(target=background_sender, args=(chat_id,), daemon=True).start()

def chat_id_in_step(chat_id, step_num):
    return chat_id in user_data and user_data[chat_id].get('step') == step_num

def chat_id_in_auto_step(chat_id, auto_step_name):
    return chat_id in user_data and user_data[chat_id].get('auto_step') == auto_step_name

@bot.message_handler(func=lambda message: chat_id_in_step(message.chat.id, 2) and message.text in ['ترند صاعد', 'ترند هابط', 'ترند متردد'])
def step_manual_trend(message):
    chat_id = message.chat.id
    user_data[chat_id]['trend_type'] = message.text
    user_data[chat_id]['step'] = 3
    times = ['تلقائي ⚡ (دقيقة واحدة)'] + [f"{i} دقيقة" for i in range(1, 11)]
    bot.send_message(chat_id, "3. اختر الوقت:", reply_markup=create_vertical_kb(times, chat_id, row=3, add_back=True))

@bot.message_handler(func=lambda message: chat_id_in_step(message.chat.id, 3) and ("دقيقة" in message.text or 'تلقائي' in message.text))
def step_manual_time(message):
    chat_id = message.chat.id
    user_data[chat_id]['time'] = "1 دقيقة (تلقائي)" if 'تلقائي' in message.text else message.text
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
    bot.send_message(chat_id, "7. حدد الشمعة الحالية:", reply_markup=create_vertical_kb(CANDLE_OPTIONS, chat_id, row=2, add_back=True))

@bot.message_handler(func=lambda message: chat_id_in_step(message.chat.id, 7) and message.text in CANDLE_OPTIONS)
def step_manual_current_candle(message):
    chat_id = message.chat.id
    user_data[chat_id]['current_candle'] = message.text
    user_data[chat_id]['step'] = 8
    bot.send_message(chat_id, "8. حدد الشموع السابقة:", reply_markup=create_vertical_kb(CANDLE_OPTIONS, chat_id, row=2, add_back=True))

@bot.message_handler(func=lambda message: chat_id_in_step(message.chat.id, 8) and message.text in CANDLE_OPTIONS)
def step_manual_final(message):
    chat_id = message.chat.id
    data = user_data[chat_id]
    duration = int(data['time'].split()[0])
    now = datetime.now()
    entry_time = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
    expiry_time = entry_time + timedelta(minutes=duration)
    
    action, strength, actual_trend = analyze_otc_trap(data['pair'], data['trend_type'], chat_id)
    
    result_text = (f"🧠 **التحليل اليدوي للـ OTC**\n"
                   f"━━━━━━━━━━━━━━━━━━━\n"
                   f"🔹 **الزوج:** {data['pair']} | {actual_trend}\n"
                   f"🔹 **الوقت المحدد:** {data['time']}\n"
                   f"🔹 **القرار المحسوب:** {action}\n"
                   f"🔹 **مؤشر الثقة الحي:** {strength}%\n"
                   f"━━━━━━━━━━━━━━━━━━━\n"
                   f"⏳ **وقت الدخول:** {entry_time.strftime('%H:%M:%S')}\n"
                   f"🏁 **وقت الانتهاء:** {expiry_time.strftime('%H:%M:%S')}")
                 
    bot.send_message(chat_id, result_text, reply_markup=get_inline_markup(chat_id), parse_mode="Markdown")
    user_data[chat_id] = {}

@bot.message_handler(func=lambda message: message.text == '⬅️ رجوع')
def handle_back(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    bot.send_message(chat_id, "القائمة الرئيسية:", reply_markup=get_inline_markup(chat_id))

bot.infinity_polling()
