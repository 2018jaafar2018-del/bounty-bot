import os
import discord
import requests
from google import genai

TOKEN = os.getenv("DISCORD_TOKEN")
API_KEY_GEMINI = os.getenv("GEMINI_API_KEY")

client_genai = genai.Client(api_key=API_KEY_GEMINI)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("البوت متصل وجاهز")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                await message.channel.send("جاري التحليل...")
                try:
                    img_data = requests.get(attachment.url).content
                    
                    # ترك اسم النموذج افتراضياً لتقوم المكتبة باختيار أحدث نموذج مدعوم تلقائياً
                    response = client_genai.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[
                            genai.types.Part.from_bytes(
                                data=img_data,
                                mime_type="image/jpeg",
                            ),
                            "حلل صورة إحصائيات لعبة One Piece Bounty Rush واستخرج النتائج والقتل والأموال."
                        ]
                    )
                    
                    await message.channel.send(response.text)
                    
                except Exception as e:
                    await message.channel.send(f"خطأ أثناء التحليل: {e}")

client.run(TOKEN)

