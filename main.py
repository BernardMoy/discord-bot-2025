import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from database import *
import asyncio
import logging

load_dotenv()

# get the token from env
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True    # Two custom intents needed
intents.members = True

# Reference the bot using this "bot"
bot = commands.Bot(command_prefix='-', intents=intents)

# Remove the default help command
bot.remove_command('help')

@bot.event
async def on_ready():
    # Connect to sqlite database
    init_db()

    # Sync bot tree for slash commands
    await bot.tree.sync()

    # Change the status message of the bot
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="-help"))

    print(f'We have logged in as {bot.user.name}')


# Load extension from cogs in the cogs folder
async def load():
    for dirpath, _, filenames in os.walk("./cogs"):
        for filename in filenames:
            if filename.endswith(".py") and filename != "__init__.py":
                # Join the dirpath with the leaf py file
                path = os.path.join(dirpath, filename)

                # Convert to python path
                path_replaced = path.replace("/", ".").replace("\\", ".")

                # Prevent paths such as ..cogs.basics.py
                if path_replaced.startswith("."):
                    path_replaced = path_replaced[2:]

                # Load extension from cogs
                await bot.load_extension(path_replaced[:-3])



logging.basicConfig(level=logging.DEBUG)
async def main():
    await load()

    # Start the bot here. Do not code below this line
    await bot.start(token)

asyncio.run(main())