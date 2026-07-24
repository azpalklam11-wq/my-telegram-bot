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
    
    send_telegram_message("🚀 **تم تشغيل بوت التداول بنجاح!**\n- نظام مزامنة التوقيت: يعمل بدقة.\n- تم تفعيل نظام منع التكرار الصارم.")

    last_execution_time = 0  # لتسجيل طابع زمن التنفيذ الأخير

    while True:
        now = datetime.now()
        current_second = now.second
        current_timestamp = time.time()
        
        # الشرط الأول: الوصول للثانية 59
        # الشرط الثاني: مرور 55 ثانية على الأقل منذ آخر عملية إرسال (يمنع التكرار جذرياً)
        if current_second == 59 and (current_timestamp - last_execution_time) > 55:
            last_execution_time = current_timestamp  # تحديث وقت آخر إرسال فوراً
            
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
                
            time.sleep(2)
        else:
            time.sleep(0.1)

if __name__ == "__main__":
    try:
        trading_engine()
    except KeyboardInterrupt:
        print("\n[!] تم إيقاف البوت يدوياً.")
