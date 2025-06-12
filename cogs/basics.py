import discord
from discord.ext import commands

# Organise collection of commands into this class
class Basics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"{ctx.author.mention} Pong! {self.bot.latency * 1000:.2f}ms")

    @commands.hybrid_command(name="dm", description="Send DM to user", with_app_command=True)
    async def dm(self, ctx, *, msg):  # msg refers to the message (Parameters) after the command / * refers to single string afterwards
        await ctx.author.send(msg)  # DM private message the author

        # Message reply with an ephemeral message
        await ctx.reply("DM Sent!", ephemeral=True)

    @commands.command()
    async def reply(self, ctx, *, msg):
        await ctx.reply(msg)  # Reply with the user message


async def setup(bot):
    await bot.add_cog(Basics(bot))