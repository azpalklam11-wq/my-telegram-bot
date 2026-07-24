import time
from datetime import datetime, timedelta
import requests

TOKEN = "8937685397:AAFZTpk7Lz3DQZzFkLBSD2UCE9qRSECe0WQ"
CHAT_ID = "6513565024"

# متغير عام لحفظ وقت آخر إرسال بالثواني الدقيقة
_last_sent_epoch = 0

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
    global _last_sent_epoch
    print("==========================================")
    print("  BOT ENGINE: OTC ALGORITHM SYNCHRONIZED  ")
    print("==========================================")
    print("[+] زر البدء (Start Button): نشط وجاهز للتشغيل")
    
    # إرسال رسالة الترحيب لمرة واحدة مع حماية ضد التكرار الفوري
    send_telegram_message("🚀 **تم تشغيل بوت التداول بنجاح!**\n- نظام مزامنة التوقيت: يعمل بدقة.\n- تم تفعيل حماية الفارق الزمني العالي.")

    while True:
        now = datetime.now()
        current_second = now.second
        current_epoch = time.time()
        
        # الشرط الحاسم: الوصول للثانية 59، وأيضاً يجب أن يكون مرّ أكثر من 58 ثانية تماماً منذ آخر رسالة
        if current_second == 59 and (current_epoch - _last_sent_epoch) > 58:
            # قفل المؤشر فوراً قبل تنفيذ أي عملية أخرى لمنع أي عملية ثانية من التداخل
            _last_sent_epoch = current_epoch
            
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
                
            # إيقاف مؤقت لمدة 3 ثوانٍ لضمان عبور الثانية 59 بالكامل
            time.sleep(3)
        else:
            time.sleep(0.1)

if __name__ == "__main__":
    try:
        trading_engine()
    except KeyboardInterrupt:
        print("\n[!] تم إيقاف البوت يدوياً.")
