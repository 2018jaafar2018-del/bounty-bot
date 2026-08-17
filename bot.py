import os
import discord
import requests
import base64
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")
API_KEY_GEMINI = os.getenv("GEMINI_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"البوت يعمل بكفاءة تامة كـ {client.user}")

def call_gemini_api(img_base64):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={API_KEY_GEMINI}"
    payload = {
        "contents": [{
            "parts": [
                {"text": (
                    "1. ابحث بدقة عن سهم 'أنت' (You) في الصورة لتحديد اللاعب المستهدف. "
                    "2. اقرأ إحصائياته الفعليّة من الصورة (القتلات K.O، السكور، والأعلام Captures). "
                    "3. اكتب رسالة حماسية جداً بحد أقصى 3 أسطر، ويجب أن تبدأ الرسالة فوراً بأقوى رقم أو إنجاز حققه، ثم أكمل الحماس. "
                    "4. ممنوع ذكر اسم اللاعب، وممنوع المقدمات. "
                    "5. إذا لم تجد صورة معركة أو سهم 'You'، أجب بـ NO_DATA."
                )},
                {"inline_data": {"mime_type": "image/jpeg", "data": img_base64}}
            ]
        }]
    }
    # تم رفع المهلة إلى 60 ثانية لتجنب الـ timeout تماماً
    response = requests.post(url, json=payload, timeout=60)
    return response.json()

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
                            await message.channel.send(analysis)
                            print("تم إرسال الرد بنجاح!")
                    else:
                        print(f"رد غير متوقع من خادم جوجل: {result}")
                            
                except Exception as e:
                    print(f"خطأ أثناء معالجة الصورة: {e}")

client.run(TOKEN)

