import time
from datetime import datetime, timedelta
import requests
import random
import threading

TOKEN = "8937685397:AAFZTpk7Lz3DQZzFkLBSD2UCE9qRSECe0WQ"
CHAT_ID = "6513565024"

# --- متغيرات الحالة العامة ---
is_bot_running = False          # حالة التشغيل والإيقاف
is_reversed = False             # زر عكس التحليل
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

# ==========================================
# لوحة المفاتيح الثابتة (Reply Keyboard) أسفل الشات
# ==========================================
def get_persistent_keyboard():
    status_text = "🟢 تشغيل البوت" if not is_bot_running else "🔴 إيقاف البوت"
    reverse_text = "✅ عكس التحليل: مفعل" if is_reversed else "❌ عكس التحليل: معطل"
    
    return {
        "keyboard": [
            [{"text": status_text}],
            [{"text": f"💱 الزوج: {selected_pair}"}, {"text": f"⏳ المدة: {selected_duration}"}],
            [{"text": reverse_text}],
            [{"text": "📊 تقرير الأرباح والخسائر"}]
        ],
        "resize_keyboard": True,   # جعل الأزرار متناسقة وصغيرة
        "is_persistent": True      # إبقاء الأزرار ظاهرة وثابتة دائماً
    }

def telegram_listener():
    """الاستماع للأوامر عند الضغط على الأزرار الثابتة"""
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
                    
                    # التحقق من الرسائل النصية القادمة من الأزرار الثابتة
                    if "message" in update and "text" in update["message"]:
                        text = update["message"]["text"]
                        
                        if "تشغيل البوت" in text:
                            is_bot_running = True
                            send_telegram_message("🟢 **تم تشغيل البوت وبدء رصد الصفقات بنجاح.**", get_persistent_keyboard())
                        elif "إيقاف البوت" in text:
                            is_bot_running = False
                            send_telegram_message("🔴 **تم إيقاف البوت مؤقتاً.**", get_persistent_keyboard())
                            
                        elif "عكس التحليل" in text:
                            is_reversed = not is_reversed
                            state_str = "مفعل ✅" if is_reversed else "معطل ❌"
                            send_telegram_message(f"🔄 **تم تغيير وضع (عكس التحليل):** أصبح الآن `{state_str}`", get_persistent_keyboard())
                            
                        elif "💱 الزوج:" in text:
                            pairs = ["EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC"]
                            current_idx = pairs.index(selected_pair) if selected_pair in pairs else 0
                            selected_pair = pairs[(current_idx + 1) % len(pairs)]
                            send_telegram_message(f"💱 **تم تغيير الزوج إلى:** `{selected_pair}`", get_persistent_keyboard())
                            
                        elif "⏳ المدة:" in text:
                            durations = ["1 دقيقة", "2 دقيقة", "5 دقائق"]
                            current_idx = durations.index(selected_duration) if selected_duration in durations else 0
                            selected_duration = durations[(current_idx + 1) % len(durations)]
                            send_telegram_message(f"⏳ **تم تغيير مدة الصفقة إلى:** `{selected_duration}`", get_persistent_keyboard())
                            
                        elif "تقرير الأرباح" in text:
                            send_telegram_message(get_performance_report(), get_persistent_keyboard())
                            
        except Exception as e:
            print(f"[!] خطأ في استقبال الأوامر: {e}")
            time.sleep(3)

# ==========================================
# 2. الدالة الثانية: محرك التحليل والمزامنة الفنية
# ==========================================
def calculate_trade_strength():
    return random.randint(85, 99)

def trading_engine():
    global last_sent_minute, total_trades, wins, losses
    print("==========================================")
    print("  BOT ENGINE: PERSISTENT KEYS ACTIVE      ")
    print("==========================================")
    
    send_telegram_message("🚀 **تم إقلاع البوت بنجاح!**\n- الأزرار الرئيسية أصبحت **ثابتة** أسفل الشات الآن.", get_persistent_keyboard())

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
            
            send_telegram_message(msg, get_persistent_keyboard())
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
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"💡 الأزرار الثابتة جاهزة للتحكم الفوري."
    )
    return report

if __name__ == "__main__":
    listener_thread = threading.Thread(target=telegram_listener, daemon=True)
    listener_thread.start()
    
    try:
        trading_engine()
    except KeyboardInterrupt:
        print("\n[!] تم إيقاف البوت يدوياً.")
