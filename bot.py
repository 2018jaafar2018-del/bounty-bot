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
    print("البوت جاهز للتركيز على صاحب الحساب")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                await message.channel.send("جاري تحليل أدائك يا بطل...")
                try:
                    img_bytes = requests.get(attachment.url).content
                    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
                    
                    # التعليمات الجديدة الموجهة للذكاء الاصطناعي
                    system_instruction = (
                        "اقرأ صورة إحصائيات لعبة One Piece Bounty Rush."
                        "ابحث عن السهم الذي يشير إلى كلمة 'You' (أنت) على يسار اسم اللاعب."
                        "عندما تجد اللاعب المشار إليه، قم بتحليل أدائه فقط:"
                        "اسم الشخصية، عدد القتلى (K.O)، السكور (Score)، ونتيجة المباراة."
                        "اكتب رسالة قصيرة جداً بحد أقصى 3 أسطر، تبارك له على أدائه (خاصة إذا فاز) وتذكره بإحصائياته بأسلوب حماسي ومشجع."
                    )
                    
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={API_KEY_GEMINI}"
                    
                    payload = {
                        "contents": [
                            {
                                "role": "user",
                                "parts": [{"text": system_instruction}]
                            },
                            {
                                "role": "model",
                                "parts": [{"text": "حسناً، سأبحث عن كلمة 'You' وأحلل أداء هذا اللاعب فقط."}]
                            },
                            {
                                "role": "user",
                                "parts": [{"inline_data": {"mime_type": "image/jpeg", "data": img_base64}}]
                            }
                        ]
                    }
                    
                    response = requests.post(url, json=payload)
                    result = response.json()
                    
                    if "candidates" in result:
                        analysis = result["candidates"][0]["content"]["parts"][0]["text"]
                        
                        # التأكد من أن الرسالة الناتجة ليست طويلة وتجاوزت الحدود
                        if len(analysis) > 2000:
                            chunks = [analysis[i:i+1900] for i in range(0, len(analysis), 1900)]
                            for chunk in chunks:
                                await message.channel.send(chunk)
                        else:
                            await message.channel.send(analysis)
                            
                    else:
                        error_msg = result.get("error", {}).get("message", str(result))
                        await message.channel.send(f"عذراً، لم أتمكن من التعرف على اللاعب المشار إليه. حاول رفع الصورة بوضوح أفضل.")
                        
                except Exception as e:
                    await message.channel.send(f"حدث خطأ أثناء التحليل: {e}")

client.run(TOKEN)

