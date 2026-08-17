import os
import discord
import requests
import base64
import asyncio
import json

TOKEN = os.getenv("DISCORD_TOKEN")

# جلب المفاتيح من المتغيرات
API_KEYS = [os.getenv("GEMINI_API_KEY"), os.getenv("GEMINI_API_KEY_2"), os.getenv("GEMINI_API_KEY_3")]
API_KEYS = [k for k in API_KEYS if k]

DATA_FILE = "stats.json"

def update_user_stats(user_id):
    data = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except: data = {}
    uid = str(user_id)
    data[uid] = data.get(uid, 0) + 1
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    return data[uid]

intents = discord.Intents.default()
intents.message_content = True # ضروري جداً
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"البوت متصل وجاهز! (عدد المفاتيح: {len(API_KEYS)})")

def call_gemini_api(img_base64):
    payload = {
        "contents": [{
            "parts": [
                {"text": "حلل الصورة وأعطِ إحصائيات اللاعب (K.O, Score, Captures). إذا لم تجد بيانات أجب بـ NO_DATA."},
                {"inline_data": {"mime_type": "image/jpeg", "data": img_base64}}
            ]
        }]
    }
    for i, api_key in enumerate(API_KEYS):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()
            print(f"المفتاح {i+1} أعطى كود {response.status_code}")
        except Exception as e:
            print(f"خطأ في الاتصال بالمفتاح {i+1}: {e}")
    return {"error": "All keys failed"}

@client.event
async def on_message(message):
    if message.author == client.user: return
    
    # سجل الطباعة للتشخيص
    if message.attachments:
        print(f"تم رصد رسالة من {message.author} تحتوي على {len(message.attachments)} صورة.")
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                try:
                    print("جاري تحميل الصورة...")
                    img_bytes = await asyncio.to_thread(requests.get, attachment.url, timeout=30)
                    img_base64 = base64.b64encode(img_bytes.content).decode("utf-8")
                    
                    print("جاري التحليل...")
                    result = await asyncio.to_thread(call_gemini_api, img_base64)
                    
                    if "candidates" in result:
                        analysis = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                        if analysis != "NO_DATA":
                            count = update_user_stats(message.author.id)
                            await message.channel.send(f"{message.author.mention}، {analysis} (الصورة {count})")
                            print("تم الرد بنجاح.")
                        else:
                            print("Gemini لم يجد بيانات في الصورة.")
                    else:
                        print(f"خطأ من Gemini: {result}")
                except Exception as e:
                    print(f"خطأ أثناء المعالجة: {e}")
    else:
        # إذا كنت تريد التأكد أن البوت يرى الرسائل العادية
        pass 

client.run(TOKEN)

