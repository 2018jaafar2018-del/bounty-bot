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
    print("البوت يعمل بكفاءة تامة")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                status_msg = await message.channel.send("جاري تحليل الإحصائيات بدقة...")
                try:
                    img_bytes = requests.get(attachment.url).content
                    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
                    
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={API_KEY_GEMINI}"
                    
                    payload = {
                        "contents": [{
                            "parts": [
                                {"text": "في هذه الصورة، يوجد سهم أبيض مكتوب عليه 'أنت' يشير إلى الصف العلوي في الفريق البرتقالي (اللاعب Demon). قم بتحليل بيانات هذا اللاعب فقط صاحب السهم بدقة. استخرج اسمه، عدد القتلات (K.O)، والسكور، واكتب رسالة تهنئة حماسية له بحد أقصى 3 أسطر."},
                                {"inline_data": {"mime_type": "image/jpeg", "data": img_base64}}
                            ]
                        }]
                    }
                    
                    response = requests.post(url, json=payload)
                    result = response.json()
                    
                    # حذف رسالة الانتظار فوراً قبل إرسال النتيجة
                    await status_msg.delete()
                    
                    if "candidates" in result:
                        analysis = result["candidates"][0]["content"]["parts"][0]["text"]
                        await message.channel.send(analysis)
                    else:
                        # في حال حدث استجابة فارغة، نتجاهلها تماماً ولا نرسل رسالة خطأ مزعجة
                        pass
                        
                except Exception as e:
                    try:
                        await status_msg.delete()
                    except:
                        pass

client.run(TOKEN)

