import discord
from discord.ext import commands
from database import *

class Qotd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="qotd",
                             description="Ask a question of the day")
    async def qotd(self, ctx, *, question=""):
        # Get the channel id that was set up for admin messaging
        message_channel = db_get_qotd_channel(ctx)

        # If the message channel does not exist, this command cannot be used
        if not message_channel:
            await ctx.send(embed=discord.Embed(
                title="Qotd channel does not exist",
                color=discord.Color(int("ff546e", 16)),
                description="Set this up using `-setqotdchannel` in the desired channel."
            ))
            return

        # If the question is empty, reject
        question = question.strip()
        if question == "":
            embed = discord.Embed(
                title="Question cannot be empty",
                description=f"Usage: `-qotd [question]`",
                color=discord.Color(int("f5429e", 16))
            )
            await ctx.send(embed=embed)
            return

        # Get the expected scheduled time
        scheduled_time = db_get_qotd_next_scheduled_time(ctx)

        # Add the question to the database

        # Reply the user
        embed = discord.Embed(
            title="Question submitted!",
            color=discord.Color(int("54ff6e", 16)),
            description=f"Your question is scheduled on <t:{scheduled_time}>",
        )
        embed.set_footer(text="It may take up to a minute for the question to show up")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Qotd(bot))