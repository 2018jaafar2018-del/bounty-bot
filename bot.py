import os
import discord
import requests
import base64
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")
API_KEY_GEMINI = os.getenv("GEMINI_API_KEY")

intents = discord.Intents.default()
intents.message_content = True # ضروري جداً لقراءة محتوى الرسالة
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"البوت يعمل الآن كـ {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    # التأكد من وجود مرفقات (صور)
    if message.attachments:
        print(f"تم استلام رسالة تحتوي على {len(message.attachments)} صورة")
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                try:
                    # تحميل الصورة
                    img_bytes = requests.get(attachment.url, timeout=10).content
                    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
                    
                    # تجهيز الطلب
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={API_KEY_GEMINI}"
                    payload = {
                        "contents": [{
                            "parts": [
                                {"text": (
                                    "1. ابحث عن سهم 'أنت' (You) في الصورة. "
                                    "2. اقرأ (القتلات K.O، السكور، والأعلام Captures). "
                                    "3. اكتب رسالة حماسية (3 أسطر كحد أقصى) تبدأ فوراً بأقوى إنجاز حققه اللاعب (القتلات أو السكور أو الأعلام). "
                                    "4. ممنوع ذكر اسم اللاعب، وممنوع المقدمات. "
                                    "5. إذا لم تجد معركة أو سهم 'You'، أجب بـ NO_DATA."
                                )},
                                {"inline_data": {"mime_type": "image/jpeg", "data": img_base64}}
                            ]
                        }]
                    }
                    
                    response = requests.post(url, json=payload, timeout=20)
                    result = response.json()
                    
                    if "candidates" in result:
                        analysis = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                        if analysis != "NO_DATA":
                            await message.channel.send(analysis)
                    else:
                        print("لم يتم العثور على candidates في رد Gemini")
                        
                except Exception as e:
                    print(f"خطأ أثناء المعالجة: {e}")

client.run(TOKEN)

