import os
import discord
import requests
import google.generativeai as genai

# قراءة الإعدادات
TOKEN = os.getenv("DISCORD_TOKEN")
API_KEY_GEMINI = os.getenv("GEMINI_API_KEY")

# إعداد مكتبة جوجل الرسمية
genai.configure(api_key=API_KEY_GEMINI)
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("البوت يعمل الآن بالمكتبة الرسمية لجوجل - جاهز للتحليل")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                await message.channel.send("جاري تحليل الإحصائيات عبر الذكاء الاصطناعي...")
                try:
                    # تحميل الصورة من ديسكورد
                    img_data = requests.get(attachment.url).content
                    
                    # إرسال الصورة للنموذج باستخدام المكتبة الرسمية
                    response = model.generate_content([
                        {
                            "mime_type": "image/jpeg",
                            "data": img_data
                        },
                        "قم بتحليل صورة إحصائيات لعبة One Piece Bounty Rush واستخرج النتائج والقتل والأموال بشكل منظم."
                    ])
                    
                    # إرسال النتيجة
                    await message.channel.send(response.text)
                    
                except Exception as e:
                    await message.channel.send(f"حدث خطأ أثناء التحليل: {e}")

client.run(TOKEN)

