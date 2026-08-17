import os
import discord
import requests
import base64
import asyncio
import io
from PIL import Image

# إعدادات البوت والمفاتيح
TOKEN = os.getenv("DISCORD_TOKEN")
API_KEYS = [
    os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3")
]
API_KEYS = [k for k in API_KEYS if k]

# الرابط الخاص بجدول بيانات Google Sheets
SHEET_URL = "https://sheetdb.io/api/v1/1wf1i8bvvglio"

def update_user_stats(user_id):
    uid = str(user_id)
    try:
        # البحث عن المستخدم في الجدول
        res = requests.get(f"{SHEET_URL}/search?User_ID={uid}")
        data = res.json()
        
        if data and len(data) > 0:
            current_count = int(data[0].get("Count", 0))
            new_count = current_count + 1
            requests.put(f"{SHEET_URL}/User_ID/{uid}", data={"Count": new_count})
            return new_count
        else:
            requests.post(SHEET_URL, data={"User_ID": uid, "Count": 1})
            return 1
    except Exception as e:
        print(f"خطأ في الاتصال بقاعدة البيانات: {e}")
        return 1

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"البوت جاهز للقتال! (متصل بـ {len(API_KEYS)} مفاتيح API)")

def process_and_encode_image(img_bytes):
    # ضغط الصورة للسرعة وتقليل استهلاك البيانات
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
        "ممنوع ذكر الاسم، ممنوع المقدمات، اجعل الرد بحد أقصى 3 أسطر. "
        "إذا لم تجد صورة معركة أو سهم 'You'، أجب بكلمة NO_DATA فقط."
    )
    
    payload = {
        "contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": img_base64}}]}]
    }

    for api_key in API_KEYS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
        try:
            response = requests.post(url, json=payload, timeout=20)
            if response.status_code == 200:
                return response.json()
        except:
            continue
    return None

@client.event
async def on_message(message):
    if message.author == client.user or not message.attachments:
        return
    
    attachment = message.attachments[0]
    if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        try:
            # تحميل ومعالجة الصورة في الخلفية حتى لا يتوقف البوت
            img_bytes = await asyncio.to_thread(lambda: requests.get(attachment.url, timeout=30).content)
            img_base64 = await asyncio.to_thread(process_and_encode_image, img_bytes)
            result = await asyncio.to_thread(call_gemini_api, img_base64)
            
            if result and "candidates" in result:
                analysis = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                if analysis != "NO_DATA":
                    count = await asyncio.to_thread(update_user_stats, message.author.id)
                    await message.channel.send(f"{message.author.mention}، {analysis} (المشاركة رقم {count})")
        except Exception as e:
            print(f"حدث خطأ أثناء المعالجة: {e}")

client.run(TOKEN)

