import discord
from discord.ext import commands

# Organise collection of commands into this class
class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="List all available commands", with_app_command=True)
    async def help(self, ctx):
        for command in self.bot.commands:
            print(command.cog_name)
            print(command.name)
            print(command.description)


async def setup(bot):
    await bot.add_cog(Help(bot))