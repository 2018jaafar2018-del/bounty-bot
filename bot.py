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
    print("البوت متصل وجاهز بالنموذج المحدث")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                await message.channel.send("جاري التحليل...")
                try:
                    img_bytes = requests.get(attachment.url).content
                    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
                    
                    # استخدام النموذج الأحدث gemini-3.5-flash المتوافق مع المفاتيح الحديثة
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={API_KEY_GEMINI}"
                    
                    payload = {
                        "contents": [
                            {
                                "parts": [
                                    {"text": "حلل صورة إحصائيات لعبة One Piece Bounty Rush واستخرج النتائج والقتل والأموال."},
                                    {
                                        "inline_data": {
                                            "mime_type": "image/jpeg",
                                            "data": img_base64
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                    
                    response = requests.post(url, json=payload)
                    result = response.json()
                    
                    if "candidates" in result:
                        analysis = result["candidates"][0]["content"]["parts"][0]["text"]
                        await message.channel.send(analysis)
                    else:
                        error_msg = result.get("error", {}).get("message", str(result))
                        await message.channel.send(f"خطأ من الخادم: {error_msg}")
                        
                except Exception as e:
                    await message.channel.send(f"حدث خطأ: {e}")

client.run(TOKEN)

