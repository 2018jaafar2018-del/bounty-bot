import os
import discord
import requests
from google import genai

# قراءة الإعدادات
TOKEN = os.getenv("DISCORD_TOKEN")
API_KEY_GEMINI = os.getenv("GEMINI_API_KEY")

# تهيئة العميل بالمكتبة الرسمية الجديدة المتوافقة مع مفاتيح AQ
client_genai = genai.Client(api_key=API_KEY_GEMINI)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("البوت يعمل بالمكتبة الرسمية الجديدة ومفاتيح AQ بنجاح - جاهز للتحليل")

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
                    
                    # إرسال الطلب باستخدام العميل الرسمي الجديد
                    response = client_genai.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[
                            genai.types.Part.from_bytes(
                                data=img_data,
                                mime_type="image/jpeg",
                            ),
                            "قم بتحليل صورة إحصائيات لعبة One Piece Bounty Rush واستخرج النتائج والقتل والأموال بشكل منظم."
                        ]
                    )
                    
                    # إرسال النتيجة
                    await message.channel.send(response.text)
                    
                except Exception as e:
                    await message.channel.send(f"حدث خطأ أثناء التحليل: {e}")

client.run(TOKEN)

