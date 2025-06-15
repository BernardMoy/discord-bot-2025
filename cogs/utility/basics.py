from collections import defaultdict

import discord
from discord.ext import commands
import os

# Organise collection of commands into this class
class Basics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = "ping", description = "Ping the bot", with_app_command=True)
    async def ping(self, ctx):
        await ctx.send(f"{ctx.author.mention} Pong! {self.bot.latency * 1000:.2f}ms")

    @commands.hybrid_command(name = "invite", description = "Get the invite link of the bot", with_app_command=True)
    async def invite(self, ctx):
        await ctx.send(embed = discord.Embed(
            title = "Bot invite link",
            description = f"[here]({os.getenv('INVITE_LINK')})",
            colour = discord.Color(int("42b6f5", 16))
        ))

    @commands.hybrid_command(name="dm", description="Send DM to user", with_app_command=True)
    async def dm(self, ctx, *, msg = ""):  # msg refers to the message (Parameters) after the command / * refers to single string afterwards
        if msg == '':
            embed = discord.Embed(
                title="Usage",
                description=f"`-dm [message]`",
                color=discord.Color(int("f5429e", 16))
            )
            await ctx.send(embed=embed)
            return

        await ctx.author.send(msg)  # DM private message the author

        # Message reply with an ephemeral message
        await ctx.reply("DM Sent!", ephemeral=True)

    @commands.hybrid_command(name="reply", description = "Reply to user's message", with_app_command=True)
    async def reply(self, ctx, *, msg = ""):
        if msg == '':
            embed = discord.Embed(
                title="Usage",
                description=f"`-reset [message]`",
                color=discord.Color(int("f5429e", 16))
            )
            await ctx.send(embed=embed)
            return

        await ctx.reply(msg)  # Reply with the user message

    @commands.hybrid_command(name="help", description="List all available commands", with_app_command=True)
    async def help(self, ctx):
        # Dict to store cogNames (Categories) : command Names
        commands_dict = defaultdict(list)
        for command in self.bot.commands:
            commands_dict[command.cog_name].append((command.name, command.description))

        # Iterate the dict to print the embed
        embed = discord.Embed(
            title="Welcome :)",
            colour=discord.Color(int("a8ccff", 16)),
            description = "Command prefix: `-`"
        )

        for key, value in commands_dict.items():
            text = ""
            for name, description in value:
                text += f"`-{name}`: {description}\n"
            embed.add_field(name=key, value=text, inline=False)

        # Add the bot name
        embed.set_author(name=self.bot.user.name,
                         icon_url=self.bot.user.avatar.url if self.bot.user.avatar is not None else "https://cdn.discordapp.com/embed/avatars/0.png")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Basics(bot))