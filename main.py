import base64
import os
import discord
import requests

# سحب التوكن والمفتاح بأمان من متغيرات البيئة في Railway
TOKEN_DISCORD = os.getenv("DISCORD_TOKEN")
API_KEY_GEMINI = os.getenv("GEMINI_API_KEY")

my_intents = discord.Intents.default()
my_intents.message_content = True
bot_client = discord.Client(intents=my_intents)


@bot_client.event
async def on_ready():
  print(f"البوت جاهز ومتحمس لتحليل إحصائياتك: {bot_client.user}")


@bot_client.event
async def on_message(message):
  if message.author == bot_client.user:
    return

  if message.attachments:
    print("تم استلام الصورة، جاري البحث عنك واستخراج إحصائياتك...")
    for item in message.attachments:
      if any(
          item.filename.lower().endswith(ext)
          for ext in [".png", ".jpg", ".jpeg", ".webp"]
      ):
        try:
          img_bytes = await item.read()
          img_b64 = base64.b64encode(img_bytes).decode("utf-8")

          url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={API_KEY_GEMINI}"

          headers = {"Content-Type": "application/json"}
          payload = {
              "contents": [{
                  "parts": [
                      {
                          "text": (
                              'Look at the image of the One Piece: Bounty Rush'
                              ' match results. 1. Find the row marked with'
                              ' "You" (the player indicator). 2. Extract their'
                              ' KOs, Captures, and Battle Score from that'
                              ' specific row. 3. Reply with a fun, enthusiastic'
                              ' message in Arabic like: "عاشت ايدك!'
                              ' إحصائياتك مجنونة: حصلت على [KOs] قتلات و'
                              ' [Captures] كابتشر وسكور [Score]! كفو!" If you'
                              ' cannot find the "You" row, just say: "ما قدرت'
                              ' أحدد إحصائياتك، ممكن صورة أوضح؟"'
                          )
                      },
                      {
                          "inline_data": {
                              "mime_type": "image/jpeg",
                              "data": img_b64,
                          }
                      },
                  ]
              }]
          }

          response = requests.post(url, headers=headers, json=payload)
          result = response.json()

          if "candidates" in result:
            answer = (
                result["candidates"][0]["content"]["parts"][0]["text"]
                .strip()
            )
            await message.reply(answer)
          else:
            error_msg = result.get("error", {}).get(
                "message", "خطأ غير معروف"
            )
            await message.reply(f"تعذر التحليل: {error_msg}")

        except Exception as e:
          print(f"خطأ برمجي: {e}")


if TOKEN_DISCORD:
  bot_client.run(TOKEN_DISCORD)
else:
  print("Error: DISCORD_TOKEN is not set in environment variables!")
