import json

import discord
from discord import Color
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import requests
from wordle_list import wordle_list
import random
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
        # await message.channel.send(hint)

        # Iterate over the currently 1025 pokemons using the poke API
        # Filter them by regex matching
        response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=10000")
        data = response.json()

        reply = ""
        for pokemon in data["results"]:
            if re.fullmatch(hint, pokemon["name"].lower()):
                reply += pokemon["name"] + "\n"

        # Create embed
        embed = discord.Embed(
            title="Pokemon match results",
            description="There are no matching pokemons!" if reply == "" else reply,
            color= discord.Color.yellow() if reply != "" else discord.Color(int("0xeb348f", 16))
        )
        await message.channel.send(embed=embed)

    # Allow listening to message continuously
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send(f"{ctx.author.mention} Pong! {bot.latency * 1000:.2f}ms")

@bot.command()
async def dm(ctx, *, msg):  # msg refers to the message (Parameters) after the command / * refers to single string afterwards
    await ctx.author.send(msg)   # DM private message the author

@bot.command()
async def reply(ctx, *, msg):
    await ctx.reply(msg)  # Reply with the user message


# Variable that stores the current wordle 5 letter word
current_wordle_word = ""

# Function to return a random, 5 letter word
def get_random_five_letter_word():
    return random.choice(wordle_list)

@bot.command()
async def wordle(ctx, guess = ""):     # Guess ia an optional argument
    """
        if not count.isnumeric():
        await ctx.send("Please enter a number.")
        return
    """

    global current_wordle_word   # Refer to the global current wordle word variable here

    # Trim the guess
    guess = guess.lower().strip()

    # Get a random five letter word if guess is not provided
    if guess == "":
        current_wordle_word = get_random_five_letter_word()
        await ctx.send(embed = discord.Embed(
            title="Wordle started!",
            description="Use -wordle guess to guess the 5 letter word.",
            color=discord.Color(int("429ef5", 16))
        ))

    elif current_wordle_word == "":
        # If a guess is provided but the current five letter word is empty, warn the user
        await ctx.send(embed=discord.Embed(
            title="You haven't started the game",
            description="Use -wordle to start a new round.",
            color=discord.Color(int("f5429e", 16))
        ))

    elif len(guess) != 5:
        # If the guess have incorrect length, warn the user
        await ctx.send(embed=discord.Embed(
            title="Invalid guess",
            description=f"{guess} is not a 5 letter word.",
            color=discord.Color(int("f5429e", 16))
        ))

    else:
        # Iterate over every position of the guessed (5 letter) word
        word_emojis = "".join([f":regional_indicator_{x}:" for x in guess])
        result = ""
        for i in range(5):
            print('yay')

        await ctx.send(f"{word_emojis}\n{result}")


# Run the bot at the end
bot.run(token, log_level = logging.DEBUG)