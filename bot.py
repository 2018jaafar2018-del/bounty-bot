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
    print("البوت يعمل الآن بالملف الجديد")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                await message.channel.send("جاري التحليل...")
                try:
                    img_data = base64.b64encode(requests.get(attachment.url).content).decode("utf-8")
                    # هذا الرابط هو الإصدار المستقر v1
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY_GEMINI}"
                    payload = {
                        "contents": [{"parts": [{"text": "حلل هذه الإحصائيات"}, {"inline_data": {"mime_type": "image/jpeg", "data": img_data}}]}]
                    }
                    response = requests.post(url, json=payload).json()
                    analysis = response["candidates"][0]["content"]["parts"][0]["text"]
                    await message.channel.send(analysis)
                except Exception as e:
                    await message.channel.send(f"خطأ: {e}")

client.run(TOKEN)
