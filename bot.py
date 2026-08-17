import os
import discord
import requests
import base64
import asyncio
import time

TOKEN = os.getenv("DISCORD_TOKEN")

# قائمة المفاتيح التي أرسلتها مدعومة مباشرة هنا
API_KEYS = [
    "AQ.Ab8RN6LcsLhUbWD0weM8L1ll3pwkTnHDjaM_K0Ve6voZotN8kQ",
    "AQ.Ab8RN6JVzktxg4hd7CVCQ0np-0HEbhSlJHUjqf0yfuPR11UoCQ",
    "AQ.Ab8RN6LlU53uCxKCBCIkqUyTUFJKOltDBjd49MVC_zfe1xiAdg"
]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"البوت يعمل بكفاءة تامة كـ {client.user} (عدد المفاتيح الجاهزة: {len(API_KEYS)})")

def call_gemini_api(img_base64):
    payload = {
        "contents": [{
            "parts": [
                {"text": (
                    "1. ابحث بدقة عن سهم 'أنت' (You) في الصورة لتحديد اللاعب المستهدف. "
                    "2. اقرأ إحصائياته الفعليّة من الصورة (القتلات K.O، السكور، والأعلام Captures). "
                    "3. اكتب رسالة حماسية جداً بحد أقصى 3 أسطر، ويجب أن تبدأ الرسالة فوراً بأقوى رقم أو إنجاز حققه. "
                    "4. ممنوع ذكر اسم اللاعب، وممنوع المقدمات. "
                    "5. إذا لم تجد صورة معركة أو سهم 'You'، أجب بـ NO_DATA."
                )},
                {"inline_data": {"mime_type": "image/jpeg", "data": img_base64}}
            ]
        }]
    }

    # المرور التلقائي على المفاتيح الواحد تلو الآخر في حال استنزاف الحصة
    for key_index, api_key in enumerate(API_KEYS):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
        
        for attempt in range(2):
            try:
                response = requests.post(url, json=payload, timeout=60)
                
                # إذا نفذ رصيد المفتاح الحالي، انتقل للمفتاح التالي فوراً
                if response.status_code == 429:
                    print(f"⚠️ المفتاح رقم {key_index + 1} استنزف حصته (429). جاري التبديل للمفتاح التالي...")
                    break
                
                if response.status_code == 503:
                    print(f"خادم جوجل مضغوط (محاولة {attempt+1} بالمفتاح {key_index+1})... انتظار 5 ثوانٍ")
                    time.sleep(5)
                    continue
                
                if response.status_code == 200:
                    return response.json()
                
                return response.json()
                
            except Exception as e:
                if attempt == 1:
                    print(f"خطأ في الاتصال بالمفتاح {key_index + 1}: {e}")
                time.sleep(5)
                
    return {"error": "All keys exhausted or failed"}

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                try:
                    print("جاري تحميل الصورة ومعالجتها...")
                    img_bytes = await asyncio.to_thread(requests.get, attachment.url, timeout=30)
                    img_base64 = base64.b64encode(img_bytes.content).decode("utf-8")
                    
                    print("جاري إرسال الصورة إلى Gemini للتحليل...")
                    result = await asyncio.to_thread(call_gemini_api, img_base64)
                    
                    if "candidates" in result:
                        analysis = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                        if analysis != "NO_DATA":
                            # الرد مع منشن صاحب الرسالة
                            await message.channel.send(f"{message.author.mention}، {analysis}")
                            print("تم إرسال الرد بنجاح!")
                    else:
                        print(f"رد غير متوقع أو أن جميع المفاتيح استنزفت: {result}")
                            
                except Exception as e:
                    print(f"خطأ أثناء معالجة الصورة: {e}")

client.run(TOKEN)

