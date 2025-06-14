import discord
from discord.ext import commands

class Qotd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="qotd",
                             description="Ask a question of the day")
    async def qotd(self, ctx, *, question=""):
        question = question.strip()
        if question == "":
            embed = discord.Embed(
                title="Question cannot be empty",
                description=f"Usage: `-qotd [question]`",
                color=discord.Color(int("f5429e", 16))
            )
            await ctx.send(embed=embed)
            return

        # Add the question to the database, and get the expected scheduled time

        # Reply the user
        embed = discord.Embed(
            title="Question submitted!",
            color=discord.Color(int("54ff6e", 16)),
            description=f"Your question is scheduled on "
        )
        embed.set_footer(text="It may take up to a minute for the question to show up")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Qotd(bot))