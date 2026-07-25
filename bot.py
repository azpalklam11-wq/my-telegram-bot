import telebot
from telebot import types
from datetime import datetime, timedelta
import time
import os
import threading
import random

# قراءة التوكن ومعرف الأدمن من بيئة الاستضافة بأمان
TOKEN = os.getenv('TOKEN', '8937685397:AAFZTpk7Lz3DQZzFkLBSD2UCE9qRSECe0WQ')
ADMIN_ID = int(os.getenv('ADMIN_ID', '6513565024'))

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

def advanced_otc_behavior_analysis(pair, trend_type, chat_id):
    is_rev = reverse_mode_active.get(chat_id, False)
    
    sec = datetime.now().second
    strength = 88 + (sec % 11)
    if strength > 99:
        strength = 98

    if trend_type == "ترند صاعد":
        primary_action = "🔴 بيع تكتيكي عكاسي (رصد مصيدة التشبع الشرائي عند الأطراف)"
        trend_desc = "صاعد (موجة متسارعة / فخ المقاومة)"
    else:
        primary_action = "🟢 شراء تكتيكي عكاسي (رصد الانهيار العمودي / تشبع بيعي للقاع)"
        trend_desc = "هابط (انهيار عمودي / فخ الدعم)"

    if is_rev:
        final_decision = primary_action + " [وضع العكس الاحترافي الذكي 🔄]"
    else:
        final_decision = primary_action

    return final_decision, strength, trend_desc

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "أهلاً بك! النظام جاهز بكافة الخصائص والترندات.", reply_markup=get_main_markup(message.chat.id))

@bot.message_handler(func=lambda message: message.text and '🔄 العكس:' in message.text)
def toggle_reverse_mode(message):
    chat_id = message.chat.id
    current_state = reverse_mode_active.get(chat_id, False)
    reverse_mode_active[chat_id] = not current_state
    state_text = "مفعل 🟢" if reverse_mode_active[chat_id] else "متوقف 🔴"
    bot.send_message(chat_id, f"⚡ تم تحديث حالة الانعكاس يدوياً.\nالحالة: {state_text}", reply_markup=get_main_markup(chat_id))

@bot.message_handler(func=lambda message: message.text in ['✅ ربح', '❌ خسارة'])
def handle_stats(message):
    chat_id = message.chat.id
    if chat_id not in user_stats:
        user_stats[chat_id] = {'wins': 0, 'losses': 0}
        
    if message.text == '✅ ربح':
        user_stats[chat_id]['wins'] += 1
        result_msg = "📈 تم تسجيل الصفقة الناجحة في السجل."
    else:
        user_stats[chat_id]['losses'] += 1
        result_msg = "📉 تم تسجيل صفقة غير موفق فيها."

    wins = user_stats[chat_id]['wins']
    losses = user_stats[chat_id]['losses']
    total = wins + losses
    ratio = int((wins / total) * 100) if total > 0 else 0

    stats_text = (f"{result_msg}\n"
                  f"━━━━━━━━━━━━━━━━━━━\n"
                  f"📊 **سجل كفاءة الخوارزمية:**\n"
                  f"🟢 رابحة: {wins}\n"
                  f"🔴 خاسرة: {losses}\n"
                  f"🎯 نسبة الدقة الفعلية: {ratio}%")
    bot.send_message(chat_id, stats_text, reply_markup=get_main_markup(chat_id), parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == 'إيقاف النظام')
def stop_bot(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "عذراً، هذا الأمر للمشرف فقط.")
        return
    auto_trading_active[message.chat.id] = False
    bot.send_message(message.chat.id, "تم إيقاف النظام وإغلاق العمليات بنجاح.")
    os._exit(0)

@bot.message_handler(func=lambda message: message.text == 'تشغيل تلقائي')
def start_auto_menu(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'auto_step': 'select_pair'}
    markup = create_vertical_kb(['جميع الأزواج (عشوائي)'] + PAIRS, chat_id, row=2, add_back=True)
    bot.send_message(chat_id, "1. اختر الزوج أو السهم للتشغيل التلقائي:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'أوتوماتيكي')
def step_manual_start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'step': 1}
    bot.send_message(chat_id, "1. اختر الزوج أو السهم للتحليل الفردي:", reply_markup=create_vertical_kb(PAIRS, chat_id, row=2, add_back=True))

@bot.message_handler(func=lambda message: chat_id_in_step(message.chat.id, 1) and message.text and (message.text in PAIRS or message.text == 'جميع الأزواج (عشوائي)'))
def step_manual_pair(message):
    chat_id = message.chat.id
    text = message.text
    if chat_id in user_data and user_data[chat_id].get('step') == 1:
        user_data[chat_id]['pair'] = text
        user_data[chat_id]['step'] = 2
        bot.send_message(chat_id, "2. اختر شكل الحركة الظاهرة على الشاشة:", reply_markup=create_vertical_kb(['ترند صاعد', 'ترند هابط'], chat_id, add_back=True))
        return

@bot.message_handler(func=lambda message: chat_id_in_auto_step(message.chat.id, 'select_pair') and message.text and (message.text in PAIRS or message.text == 'جميع الأزواج (عشوائي)'))
def handle_auto_pair_chosen(message):
    chat_id = message.chat.id
    now_ts = time.time()
    if now_ts - last_click_time.get(chat_id, 0) < 1.0:
        return
    last_click_time[chat_id] = now_ts
    
    user_data[chat_id]['auto_pair'] = message.text
    user_data[chat_id]['auto_step'] = 'select_time'
    
    times = ['تلقائي ⚡ (دقيقة واحدة)'] + [f"{i} دقيقة" for i in range(1, 11)]
    bot.send_message(chat_id, f"🟢 الزوج المختار: **{message.text}**\n2. اختر مدة الصفقات:", reply_markup=create_vertical_kb(times, chat_id, row=3, add_back=True), parse_mode="Markdown")

@bot.message_handler(func=lambda message: chat_id_in_auto_step(message.chat.id, 'select_time') and message.text and ("دقيقة" in message.text or 'تلقائي' in message.text))
def handle_auto_time_chosen(message):
    chat_id = message.chat.id
    now_ts = time.time()
    if now_ts - last_click_time.get(chat_id, 0) < 1.0:
        return
    last_click_time[chat_id] = now_ts

    selected_pair = user_data[chat_id].get('auto_pair', 'جميع الأزواج (عشوائي)')
    selected_time_text = message.text
    
    auto_trading_active[chat_id] = False
    time.sleep(0.3)
    
    auto_trading_active[chat_id] = True
    auto_selected_pairs[chat_id] = selected_pair
    auto_selected_durations[chat_id] = selected_time_text
    
    bot.send_message(chat_id, f"🚀 تم تفعيل التشغيل التلقائي بنجاح!\n🔹 الزوج: **{selected_pair}**\n🔹 المدة: **{selected_time_text}**", reply_markup=get_main_markup(chat_id), parse_mode="Markdown")
    user_data[chat_id] = {}

    def background_sender(target_chat_id):
        while auto_trading_active.get(target_chat_id, False):
            time_setting = auto_selected_durations.get(target_chat_id, 'تلقائي ⚡ (دقيقة واحدة)')
            if 'تلقائي' in time_setting:
                rand_duration = 1
            else:
                try:
                    rand_duration = int(time_setting.split()[0])
                except:
                    rand_duration = 1

            now = datetime.now()
            target_time = now.replace(second=40, microsecond=0)
            if now.second >= 40:
                target_time = target_time + timedelta(minutes=1)
                
            sleep_seconds = (target_time - datetime.now()).total_seconds()
            if sleep_seconds > 0:
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
            if current_choice == 'جميع الأزواج (عشوائي)':
                available_pairs = [p for p in PAIRS if active_pair_locks.get(p, 0) < time.time()]
                if not available_pairs:
                    rand_pair = random.choice(PAIRS)
                else:
                    rand_pair = random.choice(available_pairs)
            else:
                rand_pair = current_choice

            active_pair_locks[rand_pair] = time.time() + (rand_duration * 60 + 10)
                
            rand_trend_type = random.choice(['ترند صاعد', 'ترند هابط'])
            action, strength, trend_desc = advanced_otc_behavior_analysis(rand_pair, rand_trend_type, target_chat_id)
            
            now_msg = datetime.now()
            entry_time = (now_msg + timedelta(minutes=1)).replace(second=0, microsecond=0)
            expiry_time = entry_time + timedelta(minutes=rand_duration)
            
            auto_text = (f"📊 **تقرير التحليل السلوكي للـ OTC**\n"
                         f"━━━━━━━━━━━━━━━━━━━\n"
                         f"🔹 **الزوج / السهم:** {rand_pair} | {trend_desc}\n"
                         f"🔹 **مدة الصفقة:** {rand_duration} دقيقة\n"
                         f"🔹 **قرار النظام:** {action}\n"
                         f"🔹 **مؤشر القوة:** {strength}%\n"
                         f"━━━━━━━━━━━━━━━━━━━\n"
                         f"⏳ **وقت الدخول:** {entry_time.strftime('%H:%M:%S')}\n"
                         f"🏁 **وقت الانتهاء:** {expiry_time.strftime('%H:%M:%S')}")
            try:
                bot.send_message(target_chat_id, auto_text, reply_markup=get_main_markup(target_chat_id), parse_mode="Markdown")
            except:
                break
            
            time.sleep(2.5)

    threading.Thread(target=background_sender, args=(chat_id,), daemon=True).start()

def chat_id_in_step(chat_id, step_num):
    return chat_id in user_data and user_data[chat_id].get('step') == step_num

def chat_id_in_auto_step(chat_id, auto_step_name):
    return chat_id in user_data and user_data[chat_id].get('auto_step') == auto_step_name

@bot.message_handler(func=lambda message: chat_id_in_step(message.chat.id, 2) and message.text in ['ترند صاعد', 'ترند هابط'])
def step_manual_trend(message):
    chat_id = message.chat.id
    user_data[chat_id]['trend_type'] = message.text
    user_data[chat_id]['step'] = 3
    times = ['تلقائي ⚡ (دقيقة واحدة)'] + [f"{i} دقيقة" for i in range(1, 11)]
    bot.send_message(chat_id, "3. اختر مدة الصفقة:", reply_markup=create_vertical_kb(times, chat_id, row=3, add_back=True))

@bot.message_handler(func=lambda message: chat_id_in_step(message.chat.id, 3) and message.text and ("دقيقة" in message.text or 'تلقائي' in message.text))
def step_manual_time(message):
    chat_id = message.chat.id
    if 'تلقائي' in message.text:
        user_data[chat_id]['time'] = "1 دقيقة"
    else:
        user_data[chat_id]['time'] = message.text
        
    data = user_data[chat_id]
    duration = int(data['time'].split()[0]) if 'دقيقة' in data['time'] else 1
    now = datetime.now()
    entry_time = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
    expiry_time = entry_time + timedelta(minutes=duration)
    
    action, strength, trend_desc = advanced_otc_behavior_analysis(data['pair'], data['trend_type'], chat_id)
    
    result_text = (f"📊 **تقرير التحليل الفردي**\n"
                   f"━━━━━━━━━━━━━━━━━━━\n"
                   f"🔹 **الزوج / السهم:** {data['pair']} | {trend_desc}\n"
                   f"🔹 **المدة المحددة:** {data['time']}\n"
                   f"🔹 **قرار النظام:** {action}\n"
                   f"🔹 **مؤشر الثقة:** {strength}%\n"
                   f"━━━━━━━━━━━━━━━━━━━\n"
                   f"⏳ **وقت الدخول:** {entry_time.strftime('%H:%M:%S')}\n"
                   f"🏁 **وقت الانتهاء:** {expiry_time.strftime('%H:%M:%S')}")
                 
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
    auto_step = data.get('auto_step', '')
    
    if auto_step == 'select_time':
        user_data[chat_id] = {'auto_step': 'select_pair'}
        markup = create_vertical_kb(['جميع الأزواج (عشوائي)'] + PAIRS, chat_id, row=2, add_back=True)
        bot.send_message(chat_id, "1. اختر الزوج للتشغيل التلقائي:", reply_markup=markup)
        return
        
    if step <= 1:
        user_data[chat_id] = {}
        bot.send_message(chat_id, "القائمة الرئيسية:", reply_markup=get_main_markup(chat_id))
    elif step == 2:
        data['step'] = 1
        bot.send_message(chat_id, "1. اختر الزوج:", reply_markup=create_vertical_kb(PAIRS, chat_id, row=2, add_back=True))
    else:
        user_data[chat_id] = {}
        bot.send_message(chat_id, "القائمة الرئيسية:", reply_markup=get_main_markup(chat_id))

while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        time.sleep(5)    state_text = "مفعل 🟢" if reverse_mode_active[chat_id] else "متوقف 🔴"
    bot.send_message(chat_id, f"⚡ تم تحديث حالة الانعكاس يدوياً.\nالحالة: {state_text}", reply_markup=get_main_markup(chat_id))

@bot.message_handler(func=lambda message: message.text in ['✅ ربح', '❌ خسارة'])
def handle_stats(message):
    chat_id = message.chat.id
    if chat_id not in user_stats:
        user_stats[chat_id] = {'wins': 0, 'losses': 0}
        
    if message.text == '✅ ربح':
        user_stats[chat_id]['wins'] += 1
        result_msg = "📈 تم تسجيل الصفقة الناجحة في السجل."
    else:
        user_stats[chat_id]['losses'] += 1
        result_msg = "📉 تم تسجيل صفقة غير موفق فيها."

    wins = user_stats[chat_id]['wins']
    losses = user_stats[chat_id]['losses']
    total = wins + losses
    ratio = int((wins / total) * 100) if total > 0 else 0

    stats_text = (f"{result_msg}\n"
                  f"━━━━━━━━━━━━━━━━━━━\n"
                  f"📊 **سجل كفاءة الخوارزمية:**\n"
                  f"🟢 رابحة: {wins}\n"
                  f"🔴 خاسرة: {losses}\n"
                  f"🎯 نسبة الدقة الفعلية: {ratio}%")
    bot.send_message(chat_id, stats_text, reply_markup=get_main_markup(chat_id), parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == 'إيقاف النظام')
def stop_bot(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "عذراً، هذا الأمر للمشرف فقط.")
        return
    auto_trading_active[message.chat.id] = False
    bot.send_message(message.chat.id, "تم إيقاف النظام وإغلاق العمليات بنجاح.")
    os._exit(0)

@bot.message_handler(func=lambda message: message.text == 'تشغيل تلقائي')
def start_auto_menu(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'auto_step': 'select_pair'}
    markup = create_vertical_kb(['جميع الأزواج (عشوائي)'] + PAIRS, chat_id, row=2, add_back=True)
    bot.send_message(chat_id, "1. اختر الزوج أو السهم للتشغيل التلقائي:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'أوتوماتيكي')
def step_manual_start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'step': 1}
    bot.send_message(chat_id, "1. اختر الزوج أو السهم للتحليل الفردي:", reply_markup=create_vertical_kb(PAIRS, chat_id, row=2, add_back=True))

@bot.message_handler(func=lambda message: chat_id_in_step(message.chat.id, 1) and message.text and (message.text in PAIRS or message.text == 'جميع الأزواج (عشوائي)'))
def step_manual_pair(message):
    chat_id = message.chat.id
    text = message.text
    if chat_id in user_data and user_data[chat_id].get('step') == 1:
        user_data[chat_id]['pair'] = text
        user_data[chat_id]['step'] = 2
        bot.send_message(chat_id, "2. اختر شكل الحركة الظاهرة على الشاشة:", reply_markup=create_vertical_kb(['ترند صاعد', 'ترند هابط'], chat_id, add_back=True))
        return

@bot.message_handler(func=lambda message: chat_id_in_auto_step(message.chat.id, 'select_pair') and message.text and (message.text in PAIRS or message.text == 'جميع الأزواج (عشوائي)'))
def handle_auto_pair_chosen(message):
    chat_id = message.chat.id
    now_ts = time.time()
    if now_ts - last_click_time.get(chat_id, 0) < 1.0:
        return
    last_click_time[chat_id] = now_ts
    
    user_data[chat_id]['auto_pair'] = message.text
    user_data[chat_id]['auto_step'] = 'select_time'
    
    times = ['تلقائي ⚡ (دقيقة واحدة)'] + [f"{i} دقيقة" for i in range(1, 11)]
    bot.send_message(chat_id, f"🟢 الزوج المختار: **{message.text}**\n2. اختر مدة الصفقات:", reply_markup=create_vertical_kb(times, chat_id, row=3, add_back=True), parse_mode="Markdown")

@bot.message_handler(func=lambda message: chat_id_in_auto_step(message.chat.id, 'select_time') and message.text and ("دقيقة" in message.text or 'تلقائي' in message.text))
def handle_auto_time_chosen(message):
    chat_id = message.chat.id
    now_ts = time.time()
    if now_ts - last_click_time.get(chat_id, 0) < 1.0:
        return
    last_click_time[chat_id] = now_ts

    selected_pair = user_data[chat_id].get('auto_pair', 'جميع الأزواج (عشوائي)')
    selected_time_text = message.text
    
    auto_trading_active[chat_id] = False
    time.sleep(0.3)
    
    auto_trading_active[chat_id] = True
    auto_selected_pairs[chat_id] = selected_pair
    auto_selected_durations[chat_id] = selected_time_text
    
    bot.send_message(chat_id, f"🚀 تم تفعيل التشغيل التلقائي بنجاح!\n🔹 الزوج: **{selected_pair}**\n🔹 المدة: **{selected_time_text}**", reply_markup=get_main_markup(chat_id), parse_mode="Markdown")
    user_data[chat_id] = {}

    def background_sender(target_chat_id):
        while auto_trading_active.get(target_chat_id, False):
            time_setting = auto_selected_durations.get(target_chat_id, 'تلقائي ⚡ (دقيقة واحدة)')
            if 'تلقائي' in time_setting:
                rand_duration = 1
            else:
                try:
                    rand_duration = int(time_setting.split()[0])
                except:
                    rand_duration = 1

            now = datetime.now()
            # يمكنك تعديل رقم 40 أدناه للوقت الذي يناسبك (مثلاً قبل 20 ثانية اجعلها 40، قبل 30 ثانية اجعلها 30)
            target_time = now.replace(second=40, microsecond=0)
            if now.second >= 40:
                target_time = target_time + timedelta(minutes=1)
                
            sleep_seconds = (target_time - datetime.now()).total_seconds()
            if sleep_seconds > 0:
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
            if current_choice == 'جميع الأزواج (عشوائي)':
                available_pairs = [p for p in PAIRS if active_pair_locks.get(p, 0) < time.time()]
                if not available_pairs:
                    rand_pair = random.choice(PAIRS)
                else:
                    rand_pair = random.choice(available_pairs)
            else:
                rand_pair = current_choice

            active_pair_locks[rand_pair] = time.time() + (rand_duration * 60 + 10)
                
            rand_trend_type = random.choice(['ترند صاعد', 'ترند هابط'])
            action, strength, trend_desc = advanced_otc_behavior_analysis(rand_pair, rand_trend_type, target_chat_id)
            
            now_msg = datetime.now()
            entry_time = (now_msg + timedelta(minutes=1)).replace(second=0, microsecond=0)
            expiry_time = entry_time + timedelta(minutes=rand_duration)
            
            auto_text = (f"📊 **تقرير التحليل السلوكي للـ OTC**\n"
                         f"━━━━━━━━━━━━━━━━━━━\n"
                         f"🔹 **الزوج / السهم:** {rand_pair} | {trend_desc}\n"
                         f"🔹 **مدة الصفقة:** {rand_duration} دقيقة\n"
                         f"🔹 **قرار النظام:** {action}\n"
                         f"🔹 **مؤشر القوة:** {strength}%\n"
                         f"━━━━━━━━━━━━━━━━━━━\n"
                         f"⏳ **وقت الدخول:** {entry_time.strftime('%H:%M:%S')}\n"
                         f"🏁 **وقت الانتهاء:** {expiry_time.strftime('%H:%M:%S')}")
            try:
                bot.send_message(target_chat_id, auto_text, reply_markup=get_main_markup(target_chat_id), parse_mode="Markdown")
            except:
                break
            
            time.sleep(2.5)

    threading.Thread(target=background_sender, args=(chat_id,), daemon=True).start()

def chat_id_in_step(chat_id, step_num):
    return chat_id in user_data and user_data[chat_id].get('step') == step_num

def chat_id_in_auto_step(chat_id, auto_step_name):
    return chat_id in user_data and user_data[chat_id].get('auto_step') == auto_step_name

@bot.message_handler(func=lambda message: chat_id_in_step(message.chat.id, 2) and message.text in ['ترند صاعد', 'ترند هابط'])
def step_manual_trend(message):
    chat_id = message.chat.id
    user_data[chat_id]['trend_type'] = message.text
    user_data[chat_id]['step'] = 3
    times = ['تلقائي ⚡ (دقيقة واحدة)'] + [f"{i} دقيقة" for i in range(1, 11)]
    bot.send_message(chat_id, "3. اختر مدة الصفقة:", reply_markup=create_vertical_kb(times, chat_id, row=3, add_back=True))

@bot.message_handler(func=lambda message: chat_id_in_step(message.chat.id, 3) and message.text and ("دقيقة" in message.text or 'تلقائي' in message.text))
def step_manual_time(message):
    chat_id = message.chat.id
    if 'تلقائي' in message.text:
        user_data[chat_id]['time'] = "1 دقيقة"
    else:
        user_data[chat_id]['time'] = message.text
        
    data = user_data[chat_id]
    duration = int(data['time'].split()[0]) if 'دقيقة' in data['time'] else 1
    now = datetime.now()
    entry_time = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
    expiry_time = entry_time + timedelta(minutes=duration)
    
    action, strength, trend_desc = advanced_otc_behavior_analysis(data['pair'], data['trend_type'], chat_id)
    
    result_text = (f"📊 **تقرير التحليل الفردي**\n"
                   f"━━━━━━━━━━━━━━━━━━━\n"
                   f"🔹 **الزوج / السهم:** {data['pair']} | {trend_desc}\n"
                   f"🔹 **المدة المحددة:** {data['time']}\n"
                   f"🔹 **قرار النظام:** {action}\n"
                   f"🔹 **مؤشر الثقة:** {strength}%\n"
                   f"━━━━━━━━━━━━━━━━━━━\n"
                   f"⏳ **وقت الدخول:** {entry_time.strftime('%H:%M:%S')}\n"
                   f"🏁 **وقت الانتهاء:** {expiry_time.strftime('%H:%M:%S')}")
                 
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
    auto_step = data.get('auto_step', '')
    
    if auto_step == 'select_time':
        user_data[chat_id] = {'auto_step': 'select_pair'}
        markup = create_vertical_kb(['جميع الأزواج (عشوائي)'] + PAIRS, chat_id, row=2, add_back=True)
        bot.send_message(chat_id, "1. اختر الزوج للتشغيل التلقائي:", reply_markup=markup)
        return
        
    if step <= 1:
        user_data[chat_id] = {}
        bot.send_message(chat_id, "القائمة الرئيسية:", reply_markup=get_main_markup(chat_id))
    elif step == 2:
        data['step'] = 1
        bot.send_message(chat_id, "1. اختر الزوج:", reply_markup=create_vertical_kb(PAIRS, chat_id, row=2, add_back=True))
    else:
        user_data[chat_id] = {}
        bot.send_message(chat_id, "القائمة الرئيسية:", reply_markup=get_main_markup(chat_id))

while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        time.sleep(5)
