import os
import discord
import requests
import base64
import asyncio
import time
import json

TOKEN = os.getenv("DISCORD_TOKEN")

# جلب المفاتيح بأمان من متغيرات البيئة في Railway
API_KEYS = [
    os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3")
]
# تصفية أي مفتاح فارغ إن لم تقم بإضافته
API_KEYS = [k for k in API_KEYS if k]

# --- دالة حفظ وتحميل البيانات ---
DATA_FILE = "stats.json"

def update_user_stats(user_id):
    data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try: data = json.load(f)
            except: data = {}
    
    uid = str(user_id)
    data[uid] = data.get(uid, 0) + 1
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    return data[uid]
# -------------------------------

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"البوت يعمل بأمان تام! (عدد المفاتيح المحملة: {len(API_KEYS)})")

def call_gemini_api(img_base64):
    payload = {
        "contents": [{
            "parts": [
                {
                    "text": (
                        "1. ابحث بدقة عن سهم 'أنت' (You) في الصورة لتحديد اللاعب المستهدف. "
                        "2. اقرأ إحصائياته الفعليّة من الصورة (القتلات K.O، السكور، والأعلام Captures). "
                        "3. اكتب رسالة حماسية جداً بحد أقصى 3 أسطر، ويجب أن تبدأ الرسالة فوراً بأقوى رقم أو إنجاز حققه. "
                        "4. ممنوع ذكر اسم اللاعب، وممنوع المقدمات. "
                        "5. إذا لم تجد صورة معركة أو سهم 'You'، أجب بـ NO_DATA."
                    )
                },
                {"inline_data": {"mime_type": "image/jpeg", "data": img_base64}}
            ]
        }]
    }

    for key_index, api_key in enumerate(API_KEYS):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 429:
                print(f"⚠️ المفتاح رقم {key_index + 1} استنزف حصته، جاري التجربة بالمفتاح التالي...")
                continue
            return response.json()
        except:
            continue
    return {"error": "All keys failed"}

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                try:
                    img_bytes = await asyncio.to_thread(requests.get, attachment.url, timeout=30)
                    img_base64 = base64.b64encode(img_bytes.content).decode("utf-8")
                    result = await asyncio.to_thread(call_gemini_api, img_base64)
                    
                    if "candidates" in result:
                        analysis = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                        if analysis != "NO_DATA":
                            count = update_user_stats(message.author.id)
                            await message.channel.send(f"{message.author.mention}، {analysis} (الصورة رقم {count})")
                except Exception as e:
                    print(f"خطأ: {e}")

client.run(TOKEN)
