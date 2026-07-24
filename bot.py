import time
from datetime import datetime, timedelta

def calculate_trade_strength():
    # محاكاة حساب قوة الصفقة (بين 85% و 99%)
    import random
    return random.randint(85, 99)

def trading_engine():
    print("==========================================")
    print("  BOT ENGINE: OTC ALGORITHM SYNCHRONIZED  ")
    print("==========================================")
    print("[+] زر البدء (Start Button): نشط وجاهز للتشغيل")
    print("[ مرحلة الاختبار (Test Mode): البوت يعمل الآن بنجاح وتستجيب خوارزمية التوقيت بدقة ]\n")
    
    while True:
        now = datetime.now()
        current_second = now.second
        
        # التقاط القرار في الثانية الأخيرة لضمان عدم تأخر التحليل عن الشمعة الجديدة
        if current_second == 59:
            analysis_time = datetime.now()
            entry_time = analysis_time + timedelta(seconds=1)
            expiry_time = entry_time + timedelta(minutes=1)
            strength = calculate_trade_strength()
            
            print(f"\n[⚡ تحليل جديد متزامن]")
            print(f"-> وقت رصد القرار: {analysis_time.strftime('%H:%M:%S')}")
            print(f"-> توقيت الدخول الدقيق: {entry_time.strftime('%H:%M:%S')} (بعد ثانية واحدة)")
            print(f"-> توقيت الانتهاء: {expiry_time.strftime('%H:%M:%S')}")
            print(f"-> قوة الصفقة: {strength}%")
            
            if strength >= 90:
                print("[✔] تم استيفاء الشروط الخوارزمية بنجاح -> تنفيذ صفقة تجريبية الآن!")
            else:
                print("[✘] قوة الصفقة منخفضة -> تخطي الصفقة.")
                
            time.sleep(2)
        else:
            time.sleep(0.1)

if __name__ == "__main__":
    print("أهلاً بك! يتم تشغيل اختبار البوت الآن...")
    try:
        trading_engine()
    except KeyboardInterrupt:
        print("\n[!] تم إيقاف البوت يدوياً بنجاح.")
