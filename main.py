import os
import discord
import requests

# قراءة التوكن والمفتاح من متغيرات البيئة في Railway
TOKEN = os.getenv("DISCORD_TOKEN")
API_KEY_GEMINI = os.getenv("GEMINI_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
  print(f"البوت جاهز ومتحمس لتحليل إحصائياتك: {client.user}")


@client.event
async def on_message(message):
  # تجاهل رسائل البوت نفسه
  if message.author == client.user:
    return

  # التأكد من وجود صورة مرفقة مع الرسالة
  if message.attachments:
    for attachment in message.attachments:
      # التحقق أن المرفق صورة
      if attachment.filename.lower().endswith(
          (".png", ".jpg", ".jpeg", ".webp")
      ):
        await message.channel.send(
            "...تم استلام الصورة، جاري البحث عنك واستخراج إحصائياتك"
        )

        try:
          # تحميل الصورة كبايتات
          image_response = requests.get(attachment.url)
          if image_response.status_code != 200:
            await message.channel.send("فشل في تحميل الصورة المرفقة.")
            return

          import base64

          image_bytes = image_response.content
          image_b64 = base64.b64encode(image_bytes).decode("utf-8")

          # استخدام إصدار v1 المستقر للاتصال بـ Gemini
          url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY_GEMINI}"

          headers = {"Content-Type": "application/json"}

          payload = {
              "contents": [{
                  "parts": [
                      {
                          "text": (
                              "قم بتحليل صورة إحصائيات لعبة One Piece: Bounty"
                              " Rush واستخرج منها النتائج والقتل والأموال"
                              " وغيرها بشكل منظم."
                          )
                      },
                      {
                          "inline_data": {
                              "mime_type": "image/jpeg",
                              "data": image_b64,
                          }
                      },
                  ]
              }]
          }

          response = requests.post(url, json=payload, headers=headers)
          result = response.json()

          # استخراج الرد من نموذج جيمني
          if "candidates" in result:
            analysis_text = result["candidates"][0]["content"]["parts"][0][
                "text"
            ]
            await message.channel.send(analysis_text)
          else:
            # طباعة الخطأ القادم من واجهة برمجة التطبيقات إن وُجد
            error_msg = result.get("error", {}).get(
                "message", "خطأ غير معروف في الاستجابة"
            )
            await message.channel.send(f"تعذر التحليل: {error_msg}")

        except Exception as e:
          await message.channel.send(f"حدث خطأ أثناء المعالجة: {e}")


# تشغيل البوت
client.run(TOKEN)
