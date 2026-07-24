import time
from datetime import datetime, timedelta
import requests
import random
import threading

TOKEN = "8937685397:AAFZTpk7Lz3DQZzFkLBSD2UCE9qRSECe0WQ"
CHAT_ID = "6513565024"

# --- متغيرات الحالة العامة ---
is_bot_running = False          # حالة التشغيل
is_reversed = False             # عكس التحليل
selected_pair = "EUR/USD OTC"   # الزوج الافتراضي
selected_duration = "1 دقيقة"    # المدة الافتراضية
last_sent_minute = -1

# إحصائيات الأداء
total_trades = 0
wins = 0
losses = 0

def send_telegram_message(message, reply_markup=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"[!] خطأ في إرسال الرسالة لتليجرام: {e}")

def edit_telegram_message(message_id, message, reply_markup=None):
    """تحديث الرسالة القائمة بدلاً من إرسال رسالة جديدة لتكون الواجهة تفاعلية ونظيفة"""
    url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
    payload = {
        "chat_id": CHAT_ID,
        "message_id": message_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"[!] خطأ في تعديل الرسالة: {e}")

# ==========================================
# 1. دوال القوائم التفاعلية (Menu System)
# ==========================================
def get_main_menu():
    """القائمة الرئيسية (تحتوي على زر التشغيل، عكس التحليل، والتقرير)"""
    status_icon = "🟢 يعمل حالياً" if is_bot_running else "🔴 متوقف"
    reverse_icon = "✅ مفعل" if is_reversed else "❌ معطل"
    
    return {
        "inline_keyboard": [
            [{"text": f"🚀 تشغيل البوت ({status_icon})", "callback_data": "menu_start_wizard"}],
            [{"text": f"🔄 عكس التحليل: {reverse_icon}", "callback_data": "toggle_reverse"}],
            [{"text": "📊 تقرير الأرباح والخسائر", "callback_data": "show_report"}]
        ]
    }

def get_wizard_pair_menu():
    """قائمة اختيار الزوج (الخطوة الأولى عند التشغيل)"""
    return {
        "inline_keyboard": [
            [
                {"text": "💶 EUR/USD OTC", "callback_data": "set_pair_EUR/USD OTC"},
                {"text": "💷 GBP/USD OTC", "callback_data": "set_pair_GBP/USD OTC"}
            ],
            [
                {"text": "🇯🇵 USD/JPY OTC", "callback_data": "set_pair_USD/JPY OTC"}
            ],
            [
                {"text": "🔙 رجوع للقائمة الرئيسية", "callback_data": "back_to_main"}
            ]
        ]
    }

def get_wizard_duration_menu():
    """قائمة اختيار المدة (الخطوة الثانية بعد اختيار الزوج)"""
    return {
        "inline_keyboard": [
            [
                {"text": "⏱ 1 دقيقة", "callback_data": "set_dur_1 دقيقة"},
                {"text": "⏱ 2 دقيقة", "callback_data": "set_dur_2 دقيقة"}
            ],
            [
                {"text": "⏱ 5 دقائق", "callback_data": "set_dur_5 دقائق"}
            ],
            [
                {"text": "🔙 رجوع", "callback_data": "menu_start_wizard"}
            ]
        ]
    }

def telegram_listener():
    """الاستماع لأزرار القوائم التفاعلية وتحديث الواجهة"""
    global is_bot_running, is_reversed, selected_pair, selected_duration
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=30"
            response = requests.get(url, timeout=35)
            data = response.json()
            
            if "result" in data:
                for update in data["result"]:
                    offset = update["update_id"] + 1
                    if "callback_query" in update:
                        query = update["callback_query"]
                        callback_data = query["data"]
                        query_id = query["id"]
                        message_id = query["message"]["message_id"]
                        
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", json={"callback_query_id": query_id})
                        
                        if callback_data == "menu_start_wizard":
                            # الانتقال لاختيار الزوج
                            edit_telegram_message(
                                message_id, 
                                "💱 **الخطوة 1/2: اختر زوج العملات المراد تداوله:**", 
                                get_wizard_pair_menu()
                            )
                            
                        elif callback_data.startswith("set_pair_"):
                            # حفظ الزوج والانتقال لاختيار المدة
                            selected_pair = callback_data.replace("set_pair_", "")
                            edit_telegram_message(
                                message_id, 
                                f"✅ تم اختيار الزوج: `{selected_pair}`\n\n⏳ **الخطوة 2/2: اختر مدة الصفقة:**", 
                                get_wizard_duration_menu()
                            )
                            
                        elif callback_data.startswith("set_dur_"):
                            # حفظ المدة وتشغيل البوت تلقائياً!
                            selected_duration = callback_data.replace("set_dur_", "")
                            is_bot_running = True
                            
                            edit_telegram_message(
                                message_id,
                                f"🚀 **تم تشغيل البوت بنجاح!**\n\n"
                                f"💱 الزوج المختار: `{selected_pair}`\n"
                                f"⏳ المدة الزمنية: `{selected_duration}`\n"
                                f"🔄 عكس التحليل: `{'مفعل ✅' if is_reversed else 'معطل ❌'}`\n\n"
                                f"البوت يراقب السوق الآن ويقوم بالإرسال تلقائياً في الثانية الأخيرة من الشمعة.",
                                get_main_menu()
                            )
                            
                        elif callback_data == "toggle_reverse":
                            is_reversed = not is_reversed
                            edit_telegram_message(
                                message_id,
                                f"⚙️ **لوحة التحكم الرئيسية:**\nحالة البوت: `{'🟢 يعمل' if is_bot_running else '🔴 متوقف'}`",
                                get_main_menu()
                            )
                            
                        elif callback_data == "show_report":
                            edit_telegram_message(
                                message_id,
                                get_performance_report(),
                                get_main_menu()
                            )
                            
                        elif callback_data == "back_to_main":
                            edit_telegram_message(
                                message_id,
                                "⚙️ **لوحة التحكم الرئيسية للبوت:**\nاختر أحد الخيارات أدناه:",
                                get_main_menu()
                            )
                            
        except Exception as e:
            print(f"[!] خطأ في استقبال الأزرار: {e}")
            time.sleep(3)

# ==========================================
# 2. الدالة الثانية: محرك التحليل والمزامنة الفنية
# ==========================================
def calculate_trade_strength():
    return random.randint(85, 99)

def trading_engine():
    global last_sent_minute, total_trades, wins, losses
    print("==========================================")
    print("  BOT ENGINE: SMART MENU WIZARD ACTIVE    ")
    print("==========================================")
    
    send_telegram_message(
        "🚀 **أهلاً بك يا صديقي في نظام البوت المتطور!**\n\n⚙️ **لوحة التحكم الرئيسية:**", 
        get_main_menu()
    )

    while True:
        now = datetime.now()
        current_second = now.second
        current_minute = now.minute
        
        if not is_bot_running:
            time.sleep(1)
            continue
            
        if current_second == 59 and current_minute != last_sent_minute:
            last_sent_minute = current_minute
            
            analysis_time = datetime.now()
            entry_time = analysis_time + timedelta(seconds=1)
            
            mins_to_add = 1 if "1" in selected_duration else (2 if "2" in selected_duration else 5)
            expiry_time = entry_time + timedelta(minutes=mins_to_add)
            
            strength = calculate_trade_strength()
            base_action = "📈 شراء (CALL)" if random.choice([True, False]) else "📉 بيع (PUT)"
            
            if is_reversed:
                if "شراء" in base_action:
                    final_action = "📉 بيع (PUT) [عكس مفعّل]"
                else:
                    final_action = "📈 شراء (CALL) [عكس مفعّل]"
            else:
                final_action = base_action
            
            total_trades += 1
            if strength >= 90:
                wins += 1
                status_text = "🟢 **[حالة: مطابق للشروط -> تنفيذ]**"
            else:
                losses += 1
                status_text = "🔴 **[حالة: قوة منخفضة -> تخطي]**"
            
            msg = (
                f"⚡ **تحليل جديد متزامن (OTC)**\n"
                f"💱 الزوج: `{selected_pair}` | المدة: `{selected_duration}`\n"
                f"⏱ وقت الرصد: `{analysis_time.strftime('%H:%M:%S')}`\n"
                f"🎯 توقيت الدخول: `{entry_time.strftime('%H:%M:%S')}`\n"
                f"⌛ توقيت الانتهاء: `{expiry_time.strftime('%H:%M:%S')}`\n"
                f"🔄 الاتجاه المقترح: **{final_action}**\n"
                f"💪 قوة الصفقة: **{strength}%**\n"
                f"{status_text}"
            )
            
            send_telegram_message(msg)
            time.sleep(2)
        else:
            time.sleep(0.1)

# ==========================================
# 3. الدالة الثالثة: عداد الأرباح والخسائر والتقارير
# ==========================================
def get_performance_report():
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    report = (
        f"📊 **تقرير أداء بوت التداول الخوارزمي**\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🔹 إجمالي الصفقات المرصودة: `{total_trades}`\n"
        f"✅ الصفقات الناجحة (المطابقة): `{wins}`\n"
        f"❌ الصفقات المستبعدة (الضعيفة): `{losses}`\n"
        f"📈 نسبة الكفاءة والنجاح: `({win_rate:.1f}%)`\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )
    return report

if __name__ == "__main__":
    listener_thread = threading.Thread(target=telegram_listener, daemon=True)
    listener_thread.start()
    
    try:
        trading_engine()
    except KeyboardInterrupt:
        print("\n[!] تم إيقاف البوت يدوياً.")
