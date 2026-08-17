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
    print("البوت يعمل بثبات وبدون تجميد للأحداث")

# دالة مساعدة لتنفيذ طلب الـ API بشكل لا يجمّد البوت
def call_gemini_api(img_base64):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={API_KEY_GEMINI}"
    payload = {
        "contents": [{
            "parts": [
                {"text": (
                    "1. حدد اللاعب المستهدف حصرياً من خلال البحث عن سهم 'أنت' (You) في الصورة. "
                    "2. اقرأ إحصائياته الفعليّة (القتلات K.O، السكور، والأعلام Captures). "
                    "3. اكتب رسالة حماسية جداً بحد أقصى 3 أسطر، ويجب أن تبدأ الرسالة فوراً بأقوى رقم أو إنجاز حققه (سواء كان عدد القتلات الخرافي، أو السكور الضخم، أو عدد الأعلام)، ثم أكمل بأسلوبك الحماسي. "
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
                    # تحميل الصورة بشكل غير معرقل
                    img_bytes = await asyncio.to_thread(requests.get, attachment.url, timeout=15)
                    img_base64 = base64.b64encode(img_bytes.content).decode("utf-8")
                    
                    # استدعاء الـ API عبر نظام الـ Threads لكي لا يتوقف قلب البوت (Heartbeat)
                    result = await asyncio.to_thread(call_gemini_api, img_base64)
                    
                    if "candidates" in result:
                        analysis = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                        
                        if analysis != "NO_DATA":
                            await message.channel.send(analysis)
                    
                except Exception as e:
                    pass

client.run(TOKEN)

