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
    print("البوت يعمل بكفاءة وبدون تداخل")

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
                                    "أنت محلل فوري لصور لعبة One Piece Bounty Rush. "
                                    "انظر حصرياً إلى هذه الصورة الجديدة فقط وتجاهل أي صور سابقة تماماً. "
                                    "1. هل هذه الصورة لصفحة نتائج معركة تحتوي على إحصائيات؟ إذا لم تكن كذلك، أجب بـ NO_DATA فقط. "
                                    "2. إذا كانت هي، ابحث فوراً عن سهم 'أنت' (You) أينما كان مكانه في الصورة، وحلل بيانات ذلك اللاعب حصراً (اسم اللاعب، عدد القتلات K.O، السكور). "
                                    "3. اكتب رسالة تهنئة حماسية مخصصة لهذا اللاعب فقط بحد أقصى 3 أسطر، وبدون مقدمات مثل 'نعم هذه الصورة...'. اجعل الرد يبدأ بالتهنئة مباشرة."
                                )},
                                {"inline_data": {"mime_type": "image/jpeg", "data": img_base64}}
                            ]
                        }]
                    }
                    
                    response = requests.post(url, json=payload)
                    result = response.json()
                    
                    if "candidates" in result:
                        analysis = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                        
                        if analysis != "NO_DATA":
                            await message.channel.send(analysis)
                    
                except Exception as e:
                    pass

client.run(TOKEN)

