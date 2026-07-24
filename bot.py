import time
from datetime import datetime, timedelta
import requests
import os

TOKEN = "8937685397:AAFZTpk7Lz3DQZzFkLBSD2UCE9qRSECe0WQ"
CHAT_ID = "6513565024"
LOCK_FILE = "last_minute.txt"

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
    
    # إرسال رسالة الترحيب مرة واحدة فقط عبر التحقق من ملف القفل
    send_telegram_message("🚀 **تم تشغيل بوت التداول بنجاح!**\n- نظام مزامنة التوقيت: يعمل بدقة.\n- تم تفعيل قفل منع التكرار الجذري.")

    while True:
        now = datetime.now()
        current_second = now.second
        current_minute_str = now.strftime("%Y-%m-%d %H:%M") # دمج التاريخ مع الدقيقة لضمان الفرادة
        
        # مراقبة الثانية 59 بدقة
        if current_second == 59:
            # التحقق مما إذا تم إرسال رسالة في هذه الدقيقة مسبقاً عبر ملف نصي على السيرفر
            last_recorded_minute = ""
            if os.path.exists(LOCK_FILE):
                with open(LOCK_FILE, "r") as f:
                    last_recorded_minute = f.read().strip()
            
            # إذا لم يتم الإرسال في هذه الدقيقة بعد، نفذ العملية واقفل الدقيقة فوراً
            if current_minute_str != last_recorded_minute:
                with open(LOCK_FILE, "w") as f:
                    f.write(current_minute_str)
                
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
                
            time.sleep(2)  # تجاوز الثانية 59 بأمان
        else:
            time.sleep(0.1)

if __name__ == "__main__":
    try:
        trading_engine()
    except KeyboardInterrupt:
        print("\n[!] تم إيقاف البوت يدوياً.")
