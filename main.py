import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()

# get the token from env
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True    # Two custom intents needed
intents.members = True

# Reference the bot using this "bot"
bot = commands.Bot(command_prefix='-', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Listen to hint messages from poketwo
    if message.content.startswith("The pokémon is "):
        # Extract the hint from the message
        hint = message.content[14:-1]
        hint.replace("\\", "")  # Remove all backslashes
        await message.channel.send(hint)

    # Allow listening to message continuously
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send(f"{ctx.author.mention} Pong! {bot.latency * 1000:.2f}ms")

# Run the bot at the end
bot.run(token, log_level = logging.DEBUG)