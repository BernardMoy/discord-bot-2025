import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import requests
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