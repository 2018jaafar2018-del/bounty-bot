import os
import discord
import requests
import base64
import asyncio
import json
import io
from PIL import Image

TOKEN = os.getenv("DISCORD_TOKEN")
API_KEYS = [
    os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3")
]
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
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"البوت يعمل بكل قوة وسرعة! (عدد المفاتيح: {len(API_KEYS)})")

def process_and_encode_image(img_bytes):
    # ضغط الصورة وتقليل حجمها لتكون سريعة جداً في الإرسال والتحليل
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img.thumbnail((640, 480))
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=75)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def call_gemini_api(img_base64):
    prompt = (
        "أنت محلل محترف لألعاب القتال. انظر للصورة، ابحث عن سهم 'You'، وحدد إنجازات اللاعب (القتلات K.O، السكور، والأعلام Captures). "
        "اكتب رداً حماسياً جداً يبدأ فوراً بأقوى رقم حققه اللاعب، مع تعليق تحفيزي قصير ومثير حول أدائه. "
        "ممنوع ذكر الاسم نهائياً، ممنوع المقدمات (مثل 'إليك الإحصائيات')، اجعل الرد بحد أقصى 3 أسطر. "
        "إذا لم تجد صورة معركة أو سهم 'You'، أجب بكلمة NO_DATA فقط."
    )
    
    payload = {
        "contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": img_base64}}]}]
    }

    for i, api_key in enumerate(API_KEYS):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                continue
        except:
            continue
    return {"error": "failed"}

@client.event
async def on_message(message):
    if message.author == client.user: 
        return
    
    if message.attachments:
        attachment = message.attachments[0]
        if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            try:
                # تحميل الصورة وضغطها بشكل متزامن وآمن
                img_bytes = await asyncio.to_thread(lambda: requests.get(attachment.url, timeout=30).content)
                img_base64 = await asyncio.to_thread(process_and_encode_image, img_bytes)
                
                result = await asyncio.to_thread(call_gemini_api, img_base64)
                
                if result and "candidates" in result:
                    analysis = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if analysis != "NO_DATA":
                        count = update_user_stats(message.author.id)
                        await message.channel.send(f"{message.author.mention}، {analysis} (المشاركة رقم {count})")
            except Exception as e:
                print(f"خطأ أثناء المعالجة: {e}")

client.run(TOKEN)

