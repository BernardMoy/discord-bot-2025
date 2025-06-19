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

    @commands.hybrid_command(name = "admin", description = "Check if the current user is an admin", with_app_command=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def admin(self, ctx):
        await ctx.send(f"{ctx.author.mention} is an admin.")

    # Given a check from a list of commands.checks, determine if it is related to has_permissions(administrator = True)
    def is_admin_check(self, check):
        if not hasattr(check, "__closure__") or not check.__closure__:
            return False

        for cell in check.__closure__:
            try:
                if isinstance(cell.cell_contents, dict):
                    perms = cell.cell_contents
                    if perms.get("administrator", False):
                        return True
            except Exception as e1:
                continue
        return False

    # Given a command object, determine if it is admin only
    def is_command_admin_only(self, command):
        for check in command.checks:
            if self.is_admin_check(check):
                return True
        return False

    # Function to return the help message
    def get_help_message(self):
        # Dict to store cogNames (Categories) : command Names
        commands_dict = defaultdict(list)

        for command in self.bot.commands:
            # Check if the command has permissions restrictions (Assumed they are admin checks)
            commands_dict[command.cog_name].append(
                (command.name, command.description, self.is_command_admin_only(command)))

        # Iterate the dict to print the embed
        embed = discord.Embed(
            title="Welcome :)",
            colour=discord.Color(int("a8ccff", 16)),
            description="Command prefix: `-` \n Admin-only commands are indicated with 🔒 "
        )

        for key, value in commands_dict.items():
            # Sort the values to ensure regular commands come first
            value.sort(key=lambda x: x[2])

            text = ""
            for name, description, is_admin_only in value:
                text += f"`-{name}`: {description}\n" if not is_admin_only else f"`-{name}` 🔒: {description}\n"
            embed.add_field(name=key, value=text, inline=False)

        # Add the bot name
        embed.set_author(name=self.bot.user.name,
                         icon_url=self.bot.user.avatar.url if self.bot.user.avatar is not None else "https://cdn.discordapp.com/embed/avatars/0.png")

        return embed

    # Return a list of available commands, classified and sorted
    @commands.hybrid_command(name="help", description="List all available commands", with_app_command=True)
    async def help(self, ctx):
        embed = self.get_help_message()
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if self.bot.user in message.mentions:
            embed = self.get_help_message()
            await message.channel.send(embed = embed)

async def setup(bot):
    await bot.add_cog(Basics(bot))