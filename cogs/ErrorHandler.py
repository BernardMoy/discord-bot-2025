import logging

import discord
from discord.ext import commands

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        # Handle admin errors
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(
                title="Missing permissions",
                color=discord.Color(int("fc6f03", 16)),
                description="You do not have permissions to execute this command."
            ))

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(embed=discord.Embed(
                title="Server only command",
                color=discord.Color(int("fc6f03", 16)),
                description="You cannot execute this command in private messages."
            ))

        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.send(embed=discord.Embed(
                title="Private message only command",
                color=discord.Color(int("fc6f03", 16)),
                description="You cannot execute this command in a server."
            ))

        else:
            logging.error(error)

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))