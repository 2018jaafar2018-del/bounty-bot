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
    print(f"البوت يعمل بكفاءة تامّة كـ {client.user}")

def call_gemini_api(img_base64):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={API_KEY_GEMINI}"
    payload = {
        "contents": [{
            "parts": [
                {"text": (
                    "1. ابحث بدقة عن سهم 'أنت' (You) في الصورة لتحديد اللاعب المستهدف. "
                    "2. اقرأ إحصائياته الفعليّة من الصورة (القتلات K.O، السكور، والأعلام Captures). "
                    "3. اكتب رسالة حماسية جداً بحد أقصى 3 أسطر، **ويجب أن تبدأ الرسالة فوراً بأقوى رقم أو إنجاز حققه** (سواء كان عدد القتلات العالي، أو السكور الضخم، أو الأعلام)، ثم أكمل الحماس. "
                    "4. ممنوع منعاً باتاً ذكر اسم اللاعب، وممنوع وضع أي مقدمات عامة. "
                    "5. إذا لم تجد صورة معركة أو لم تجد السهم، أجب بكلمة واحدة: NO_DATA."
                )},
                {"inline_data": {"mime_type": "image/jpeg", "data": img_base64}}
            ]
        }]
    }
    response = requests.post(url, json=payload, timeout=20)
    return response.json()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                try:
                    img_bytes = await asyncio.to_thread(requests.get, attachment.url, timeout=15)
                    img_base64 = base64.b64encode(img_bytes.content).decode("utf-8")
                    
                    result = await asyncio.to_thread(call_gemini_api, img_base64)
                    
                    if "candidates" in result:
                        analysis = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                        if analysis != "NO_DATA":
                            await message.channel.send(analysis)
                            
                except Exception as e:
                    print(f"خطأ أثناء معالجة الصورة: {e}")

client.run(TOKEN)

