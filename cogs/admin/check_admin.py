import discord
from discord.ext import commands

class CheckAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description = "Check if the current user is an admin")
    @commands.has_permissions(administrator=True)
    async def admin(self, ctx):
        await ctx.send(f"{ctx.author.mention} is an admin.")


    @admin.error
    async def admin_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(
            title="Missing permissions",
            color=discord.Color(int("fc6f03", 16)),
            description="You do not have permissions to execute this command."
        ))

async def setup(bot):
    await bot.add_cog(CheckAdmin(bot))
