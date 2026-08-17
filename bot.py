import os
import discord
import requests
import base64

TOKEN = os.getenv("DISCORD_TOKEN")
API_KEY_GEMINI = os.getenv("GEMINI_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("البوت يعمل بوضع التصفية الذكية والتحليل الدقيق")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                try:
                    img_bytes = requests.get(attachment.url).content
                    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
                    
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={API_KEY_GEMINI}"
                    
                    payload = {
                        "contents": [{
                            "parts": [
                                {"text": (
                                    "قم بتحليل الصورة. "
                                    "1. هل هذه الصورة لصفحة نتائج معركة في لعبة One Piece Bounty Rush تحتوي على إحصائيات (K.O/Score)؟ "
                                    "2. إذا لم تكن كذلك، أجب بكلمة واحدة فقط: NO_DATA. "
                                    "3. إذا كانت هي، ابحث عن السهم المكتوب عليه 'أنت' (You) في الصف العلوي، وحلل بيانات هذا اللاعب فقط (الاسم، القتلات، السكور) واكتب رسالة تهنئة حماسية بحد أقصى 3 أسطر."
                                )},
                                {"inline_data": {"mime_type": "image/jpeg", "data": img_base64}}
                            ]
                        }]
                    }
                    
                    response = requests.post(url, json=payload)
                    result = response.json()
                    
                    if "candidates" in result:
                        analysis = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                        
                        # البوت يرسل الرد فقط إذا لم تكن النتيجة NO_DATA
                        if analysis != "NO_DATA":
                            await message.channel.send(analysis)
                    
                except Exception as e:
                    # صمت تام في حال حدوث أي خطأ تقني للحفاظ على نظافة الشات
                    pass

client.run(TOKEN)

