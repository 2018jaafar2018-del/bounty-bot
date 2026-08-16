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
    print("البوت يعمل والتحليل دقيق")

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
                    
                    # الـ Prompt الجديد يركز على مكان السهم بدقة
                    payload = {
                        "contents": [{
                            "parts": [
                                {"text": "حلل صورة إحصائيات One Piece Bounty Rush. ركز فقط على اللاعب الذي يوجد بجانب اسمه سهم يشير لليسار (مكتوب عنده 'You'). لا تحلل أي لاعب آخر. استخرج اسمه وسكور القتل والأموال، واكتب رسالة تهنئة حماسية له بحد أقصى 3 أسطر."},
                                {"inline_data": {"mime_type": "image/jpeg", "data": img_base64}}
                            ]
                        }]
                    }
                    
                    response = requests.post(url, json=payload)
                    result = response.json()
                    
                    # حذف رسالة "جاري التحليل"
                    await status_msg.delete()
                    
                    if "candidates" in result:
                        analysis = result["candidates"][0]["content"]["parts"][0]["text"]
                        await message.channel.send(analysis)
                    else:
                        # حذفنا الـ print الخاص بالـ error لكي لا يظهر للمستخدم
                        await message.channel.send("عذراً، لم أستطع قراءة البيانات، حاول رفع الصورة مرة أخرى.")
                        
                except Exception as e:
                    await status_msg.delete()
                    await message.channel.send(f"حدث خطأ أثناء الاتصال بالخادم.")

client.run(TOKEN)

