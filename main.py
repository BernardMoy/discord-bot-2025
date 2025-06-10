import json

import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import requests
from wordle_list import wordle_list
import random
import re
from database import *

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
    # Connect to sqlite database
    init_db()

    # Sync bot tree for slash commands
    await bot.tree.sync()

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

@bot.hybrid_command(name="dm", description="Send DM to user", with_app_command=True)
async def dm(ctx, *, msg):  # msg refers to the message (Parameters) after the command / * refers to single string afterwards
    await ctx.author.send(msg)   # DM private message the author

    # Message reply with an ephemeral message
    await ctx.reply("DM Sent!", ephemeral=True)

@bot.command()
async def reply(ctx, *, msg):
    await ctx.reply(msg)  # Reply with the user message


# Variable that stores the current wordle 5 letter word
current_wordle_word = ""
# Variable that stores the current wordle result
current_wordle_result = ""
# Variable that stores the number of tries
current_wordle_tries = 0
# Store all used letters
current_wordle_dict = set()

# Function to return a random, 5 letter word
def get_random_five_letter_word():
    word = random.choice(list(wordle_list))

    # Print the word
    print(f"New wordle round started: {word}")
    return word


@bot.command()
async def wordle(ctx, guess=""):

    def reset_wordle():
        global current_wordle_word
        global current_wordle_result
        global current_wordle_tries
        global current_wordle_dict

        current_wordle_word = ""
        current_wordle_result = ""
        current_wordle_tries = 0
        current_wordle_dict.clear()

    def get_keyboard():
        global current_wordle_dict
        keyboard = ""
        for char in "qwertyuiop":
            keyboard += f":regional_indicator_{char}: " if char not in current_wordle_dict else ":black_large_square: "
        keyboard += '\n    '

        for char in "asdfghjkl":
            keyboard += f":regional_indicator_{char}: " if char not in current_wordle_dict else ":black_large_square: "
        keyboard += '\n        '

        for char in "zxcvbnm":
            keyboard += f":regional_indicator_{char}: " if char not in current_wordle_dict else ":black_large_square: "
        keyboard += '\n'

        return keyboard


    global current_wordle_word   # Refer to the global current wordle word variable here
    global current_wordle_result
    global current_wordle_tries
    global current_wordle_dict

    # Trim the guess
    guess = guess.lower().strip()

    # If guess is not provided, send usage message
    if guess == '':
        embed = discord.Embed(
            title="Usage",
            description=f"`-wordle [guess]` or \n `-wordle -reset` to reset",
            color=discord.Color(int("f5429e", 16))
        )
        await ctx.send(embed=embed)


    # If guess is "-reset", reset it
    elif guess == "-reset":
        reset_wordle()
        current_wordle_word = get_random_five_letter_word()

        embed=discord.Embed(
            title=f"Wordle has been reset",
            description="Use -wordle `xxxxx` for your first guess",
            color=discord.Color(int("42b0f5", 16))
        )

        await ctx.send(embed=embed)


    elif len(guess) != 5 or guess not in wordle_list:
        # If the guess has incorrect length or is not a valid word, warn the user
        embed=discord.Embed(
            title="Invalid guess",
            description=f"`{guess}` is not a 5 letter word. \n\n {get_keyboard()}",
            color=discord.Color(int("f5429e", 16))
        )

        # Set the footer by including the keyboard and the reset warning
        embed.set_footer(text="Use -wordle -reset to reset the game")
        await ctx.send(embed=embed)

    else:
        # If the current wordle word is empty, get a new random five letter word
        if current_wordle_word == "":
            reset_wordle()
            current_wordle_word = get_random_five_letter_word()

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

                # Add the used character to the dict
                current_wordle_dict.add(guess[i])

        # Append to the global wordle result
        current_wordle_result += f"\n {word_emojis} \n{result} \n"

        # Add the tries
        current_wordle_tries += 1

        embed=discord.Embed(
            title=f"Wordle {current_wordle_tries}/6",
            description=f"{current_wordle_result} \n\n {get_keyboard()}",
            color=discord.Color(int("42b0f5", 16))
        )

        embed.set_footer(text="Use -wordle -reset to reset the game")
        await ctx.send(embed=embed)

        # If the guess is correct, send message
        if guess == current_wordle_word:
            await ctx.send(embed=discord.Embed(
                title=f"You won!",
                description=ctx.author.mention,
                color=discord.Color(int("93f542", 16))
            ))

            # Add to database
            db_put_wordle_win(ctx, current_wordle_word)

            # Reset the wordle for the next round
            reset_wordle()

        # If the number of tries is 6, end the game
        elif current_wordle_tries == 6:
            await ctx.send(embed=discord.Embed(
                title=f"You lost!",
                description=f"The word was `{current_wordle_word}`.",
                color=discord.Color(int("f57b42", 16))
            ))

            reset_wordle()


# Generate a leaderboard from the SQL query result
def generate_leaderboard(rows):
    leaderboard_text = ""
    for i in range(len(rows)):
        user_id, count = rows[i]

        # Show the 1, 2, 3 badges
        if i == 0:
            leaderboard_text += ":first_place:"
        elif i == 1:
            leaderboard_text += ":second_place:"
        elif i == 2:
            leaderboard_text += ":third_place:"
        else:
            leaderboard_text += f"{i+1}. "

        # Add the user mention and the count
        leaderboard_text += f"<@{user_id}> - {count}\n"
    return leaderboard_text

# Show the leaderboard of different games
# Of the table user_<game> in the sql schema
@bot.command()
async def leaderboard(ctx, category = ""):
    if category == "wordle":
        rows = db_get_wordle_leaderboard(ctx)
        embed = discord.Embed(
            title=f"Wordle leaderboard",
            description=generate_leaderboard(rows),
            color=discord.Color(int("833efa", 16))
        )
        await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def admin(ctx):
    await ctx.send(f"{ctx.author.mention} is an admin.")

@admin.error
async def admin_error(ctx, error):
    await ctx.send(embed = discord.Embed(
        title="Missing permissions",
        color=discord.Color(int("fc6f03", 16)),
        description="You do not have permissions to execute this command."
    ))

# Set the admin message channel
@bot.command()
@commands.has_permissions(administrator=True)
async def setadminmessagechannel(ctx):
    result = db_set_admin_messages_channel(ctx)
    if result:
        await ctx.send(embed=discord.Embed(
            title="Admin message channel set",
            color=discord.Color(int("54ff6e", 16)),
            description="Use -telladmin [message] to tell messages to admins, which will appear in this channel."
        ))


# Remove the admin message channel


# Run the bot at the end
bot.run(token, log_level = logging.DEBUG)