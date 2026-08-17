import os
import discord

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print(f"تم استلام رسالة: {message.content}") # هذه ستظهر في Logs فوراً
    if message.attachments:
        await message.channel.send("البوت يعمل واستلمت الصورة!")

client.run(os.getenv("DISCORD_TOKEN"))

