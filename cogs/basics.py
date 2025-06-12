import discord
from discord.ext import commands

# Organise collection of commands into this class
class Basics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"{ctx.author.mention} Pong! {self.bot.latency * 1000:.2f}ms")

async def setup(bot):
    await bot.add_cog(Basics(bot))