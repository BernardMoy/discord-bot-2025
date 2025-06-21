import discord
from discord.ext import commands
from main import db

# Generate a leaderboard from the SQL query result
def generate_leaderboard(rows):
    # Check if the table is empty
    if len(rows) == 1 and rows[0] == (None, 0) or len(rows) == 0:
        return "There are no players in this server yet! "

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

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Show the leaderboard of different games
    # Of the table user_<game> in the sql schema
    @commands.guild_only()
    @commands.hybrid_command(name = "leaderboard", description = "Show the leaderboard of different games", with_app_command=True)
    async def leaderboard(self, ctx, category=""):
        if category == '':
            embed = discord.Embed(
                title="Usage",
                description=f"`-leaderboard [game]`",
                color=discord.Color(int("f5429e", 16))
            )
            await ctx.send(embed=embed)
            return

        if category == "wordle":
            rows = db.db_get_wordle_leaderboard(ctx)
            embed = discord.Embed(
                title=f"Wordle leaderboard",
                description=generate_leaderboard(rows),
                color=discord.Color(int("833efa", 16))
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))