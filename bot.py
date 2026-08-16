import base64
import discord
import requests

TOKEN_DISCORD = (
    "MTUzMzU4NzE1OTk1NTUzNzk2Mw.GVry-i.FAlpos-LKjc9JORVjzTLi-Hn9ng3NMvgIWl0Jw"
)
API_KEY_GEMINI = "AQ.Ab8RN6I0SCiFt09JjORsW21Spxy0OERphstsGOfjbDql9SwqEA"

my_intents = discord.Intents.default()
my_intents.message_content = True
bot_client = discord.Client(intents=my_intents)


@bot_client.event
async def on_ready():
  print(f"البوت يعمل الآن بختصار وإحداثيات سريعة: {bot_client.user}")


@bot_client.event
async def on_message(message):
  if message.author == bot_client.user:
    return

  if message.attachments:
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
                              'Analyze this match screenshot for One Piece:'
                              ' Bounty Rush. 1. If not a valid match result,'
                              ' reply strictly "IGNORE". 2. Find the row marked'
                              ' with "You". Extract KOs, Captures, and Battle'
                              ' Score. 3. CRITICAL: Reply in maximum 3 short'
                              ' lines in Arabic. Be punchy, hype, varied, and'
                              ' creative. Highlight the top stat (KOs or'
                              ' Captures) and mention the score ONLY if it is'
                              ' above 8000.'
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
            if answer.upper() != "IGNORE":
              await message.reply(answer)

        except Exception as e:
          print(f"خطأ: {e}")


bot_client.run(TOKEN_DISCORD)
