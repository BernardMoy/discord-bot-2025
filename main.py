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
# Variable that stores the current wordle result
current_wordle_result = ""
# Variable that stores the number of tries
current_wordle_tries = 0

# Function to return a random, 5 letter word
def get_random_five_letter_word():
    return random.choice(list(wordle_list))

@bot.command()
async def wordle(ctx, guess):
    """
        if not count.isnumeric():
        await ctx.send("Please enter a number.")
        return
    """

    global current_wordle_word   # Refer to the global current wordle word variable here
    global current_wordle_result
    global current_wordle_tries

    # Trim the guess
    guess = guess.lower().strip()

    # If guess is "-reset", reset it
    if guess == "-reset":
        current_wordle_word = get_random_five_letter_word()
        current_wordle_result = ""
        current_wordle_tries = 0

        embed=discord.Embed(
            title=f"Wordle reset",
            description="Use -wordle xxxxx for your first guess",
            color=discord.Color(int("42b0f5", 16))
        )

        await ctx.send(embed=embed)


    # Get a random five letter word if guess is not provided
    elif len(guess) != 5 or guess not in wordle_list:
        # If the guess have incorrect length, warn the user
        embed=discord.Embed(
            title="Invalid guess",
            description=f"{guess} is not a 5 letter word.",
            color=discord.Color(int("f5429e", 16))
        )

        embed.set_footer(text="Use -wordle -reset to reset the game")

        await ctx.send(embed=embed)

    else:
        # If the current wordle word is empty, get a new random five letter word
        if current_wordle_word == "":
            current_wordle_word = get_random_five_letter_word()
            current_wordle_result = ""
            current_wordle_tries = 0

        # Iterate over every position of the guessed (5 letter) word
        word_emojis = "".join([f":regional_indicator_{x}:" for x in guess])
        result = ""
        for i in range(5):
            if current_wordle_word[i] == guess[i]:
                result += ":green_square:"
            elif guess[i] in list(current_wordle_word):
                result += ":yellow_square:"
            else:
                result += ":black_large_square:"

        # Append to the global wordle result
        current_wordle_result += "\n" + word_emojis + "\n" + result + "\n"

        # Add the tries
        current_wordle_tries += 1

        embed=discord.Embed(
            title=f"Wordle {current_wordle_tries}/6",
            description=current_wordle_result,
            color=discord.Color(int("42b0f5", 16))
        )

        embed.set_footer(text="Use -wordle -reset to reset the game")
        await ctx.send(embed=embed)

        # If the guess is correct, send message
        if guess == current_wordle_word:
            await ctx.send(embed=discord.Embed(
                title=f"You won!",
                description=f":)",
                color=discord.Color(int("93f542", 16))
            ))

            current_wordle_word = ""
            current_wordle_result = ""
            current_wordle_tries = 0

        # If the number of tries is 6, end the game
        elif current_wordle_tries == 6:
            await ctx.send(embed=discord.Embed(
                title=f"You lost!",
                description=f"The word was {current_wordle_word}.",
                color=discord.Color(int("f57b42", 16))
            ))

            current_wordle_word = ""
            current_wordle_result = ""
            current_wordle_tries = 0


# Run the bot at the end
bot.run(token, log_level = logging.DEBUG)