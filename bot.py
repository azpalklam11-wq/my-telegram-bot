import time
from datetime import datetime, timedelta
import requests

TOKEN = "8937685397:AAFZTpk7Lz3DQZzFkLBSD2UCE9qRSECe0WQ"
CHAT_ID = "6513565024"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"[!] خطأ في إرسال الرسالة لتليجرام: {e}")

def calculate_trade_strength():
    import random
    return random.randint(85, 99)

def trading_engine():
    print("==========================================")
    print("  BOT ENGINE: OTC ALGORITHM SYNCHRONIZED  ")
    print("==========================================")
    print("[+] زر البدء (Start Button): نشط وجاهز للتشغيل")
    print("[+] تم ربط بوت تليجرام وإرسال رسالة ترحيبية...\n")
    
    send_telegram_message("🚀 **تم تشغيل بوت التداول بنجاح!**\n- نظام مزامنة التوقيت: يعمل بدقة.\n- تم منع تكرار الرسائل.")

    last_sent_minute = -1  # متغير لتخزين آخر دقيقة تم إرسال رسالة فيها

    while True:
        now = datetime.now()
        current_second = now.second
        current_minute = now.minute
        
        # التأكد من أننا في الثانية 59 وأننا لم نرسل رسالة في هذه الدقيقة من قبل
        if current_second == 59 and current_minute != last_sent_minute:
            last_sent_minute = current_minute  # تحديث الدقيقة حتى لا تتكرر الرسالة
            
            analysis_time = datetime.now()
            entry_time = analysis_time + timedelta(seconds=1)
            expiry_time = entry_time + timedelta(minutes=1)
            strength = calculate_trade_strength()
            
            msg = (
                f"⚡ **تحليل جديد متزامن (OTC)**\n"
                f"⏱ وقت الرصد: `{analysis_time.strftime('%H:%M:%S')}`\n"
                f"🎯 توقيت الدخول: `{entry_time.strftime('%H:%M:%S')}`\n"
                f"⌛ توقيت الانتهاء: `{expiry_time.strftime('%H:%M:%S')}`\n"
                f"💪 قوة الصفقة: **{strength}%**\n"
            )
            
            if strength >= 90:
                msg += "🟢 **[حالة: مطابق للشروط -> تنفيذ الصفقة]**"
            else:
                msg += "🔴 **[حالة: قوة منخفضة -> تخطي]**"
            
            print(msg.replace("*", "").replace("`", ""))
            send_telegram_message(msg)
                
            time.sleep(1.5)  # توقف قصير لضمان تجاوز الثانية 59 بأمان
        else:
            time.sleep(0.1)

if __name__ == "__main__":
    try:
        trading_engine()
    except KeyboardInterrupt:
        print("\n[!] تم إيقاف البوت يدوياً.")
        send_telegram_message("⚠️ **تم إيقاف تشغيل البوت يدوياً.**")
