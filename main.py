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
import asyncio

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

    # Change the status message of the bot
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="-help"))

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

# Load extension from cogs in the cogs folder
async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f"cogs.{filename[:-3]}")



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
            description="Use `-telladmin [message]` to tell messages to admins, which will appear in this channel."
        ))


# Remove the admin message channel
@bot.command()
@commands.has_permissions(administrator=True)
async def removeadminmessagechannel(ctx):
    result = db_remove_admin_messages_channel(ctx)
    if result:
        await ctx.send(embed=discord.Embed(
            title="Admin message channel removed",
            color=discord.Color(int("ffcc54", 16)),
            description="Users can no longer use `-telladmin` until another channel is set."
        ))


# Tell admin messages to the channel that was set up
@bot.hybrid_command(name="telladmin", description="Tell admins a message. Your message will not be shown to others.")
async def telladmin(ctx, *, message=""):
    # Get the channel id that was set up for admin messaging
    message_channel = db_get_admin_messages_channel(ctx)

    # trim the message
    message = message.strip()

    # If the message channel does not exist, this command cannot be used
    if not message_channel:
        await ctx.send(embed=discord.Embed(
            title="Admin message channel not exist",
            color=discord.Color(int("ff546e", 16)),
            description="Set this up using `-setadminmessagechannel` in the desired channel."
        ))
        return

    # If message is none, reject it
    if not message:
        await ctx.send(embed=discord.Embed(
            title="Message cannot be empty",
            color=discord.Color(int("ff546e", 16)),
            description="Usage: `-telladmin [message]`"
        ))
        return

    # Send the user's message in the message channel
    channel = bot.get_channel(message_channel)
    embed = discord.Embed(
        title = "New Message",
        description=message,
        color=discord.Color(int("ffe354", 16))
    )
    embed.set_footer(text=ctx.author.name, icon_url=ctx.author.display_avatar.url)  # User info in footer
    await channel.send(embed=embed)


    # If the user is using slash command, reply them
    # Else DM them
    if ctx.interaction is not None:   # Check if user is using SLASH COMMAND (APP COMMANDS)
        await ctx.reply("Message sent!", ephemeral = True)

    else:
        # Afterwards, delete the user message
        await ctx.message.delete()


        # Send dm
        await ctx.author.send(embed =discord.Embed(
            title = "Message sent to admins",
            description=message,
            color=discord.Color(int("ffe354", 16))
        ))

async def main():
    await load()
    await bot.start(token)

asyncio.run(main())