import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import requests
import re

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
        hint = message.content[15:-1].lower()
        hint = hint.replace("\_", ".")  # Replace _ with . for regex matching
        await message.channel.send(hint)

        # Iterate over the currently 1025 pokemons using the poke API
        # Filter them by regex matching
        response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=10000")
        data = response.json()

        reply = ""
        for pokemon in data["results"]:
            if re.fullmatch(hint, pokemon["name"].lower()):
                reply += pokemon["name"] + "\n"

        # Create embed 
        await message.channel.send(reply)

    # Allow listening to message continuously
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send(f"{ctx.author.mention} Pong! {bot.latency * 1000:.2f}ms")

@bot.command()
async def dm(ctx, *, msg):  # msg refers to the message (Parameters) after the command
    await ctx.author.send(msg)   # DM private message the author

@bot.command()
async def reply(ctx, *, msg):
    await ctx.reply(msg)  # Reply with the user message

# Run the bot at the end
bot.run(token, log_level = logging.DEBUG)