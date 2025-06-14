import discord
from discord.ext import commands
from database import *

class Admin(commands.Cog):
    """ Stores all commands that can ONLY be executed by admins """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description = "Check if the current user is an admin")
    @commands.has_permissions(administrator=True)
    async def admin(self, ctx):
        await ctx.send(f"{ctx.author.mention} is an admin.")

    # Set the admin message channel
    @commands.command(description = "Set the current channel to be the admin message channel")
    @commands.has_permissions(administrator=True)
    async def setadminmessagechannel(self, ctx):
        result = db_set_admin_messages_channel(ctx)
        if result:
            await ctx.send(embed=discord.Embed(
                title="Admin message channel set",
                color=discord.Color(int("54ff6e", 16)),
                description="Use `-telladmin [message]` to tell messages to admins, which will appear in this channel."
            ))

    # Remove the admin message channel
    @commands.command(description = "Remove the admin message channel of the server")
    @commands.has_permissions(administrator=True)
    async def removeadminmessagechannel(self, ctx):
        result = db_remove_admin_messages_channel(ctx)
        if result:
            await ctx.send(embed=discord.Embed(
                title="Admin message channel removed",
                color=discord.Color(int("ffcc54", 16)),
                description="Users can no longer use `-telladmin` until another channel is set."
            ))

    # Set the qotd message channel
    @commands.command(description = "Set the current channel to be the qotd message channel")
    @commands.has_permissions(administrator=True)
    async def setqotdchannel(self, ctx):
        result = db_set_qotd_channel(ctx)
        if result:
            await ctx.send(embed=discord.Embed(
                title="QOTD channel set",
                color=discord.Color(int("54ff6e", 16)),
                description="Use `-qotd [question]` to ask QOTDs, which will appear in this channel."
            ))

    # Remove the qotd message channel
    @commands.command(description = "Remove the qotd message channel of the server")
    @commands.has_permissions(administrator=True)
    async def removeqotdchannel(self, ctx):
        result = db_remove_qotd_channel(ctx)
        if result:
            await ctx.send(embed=discord.Embed(
                title="QOTD channel removed",
                color=discord.Color(int("ffcc54", 16)),
                description="Users can no longer use `-qotd` until another channel is set."
            ))



    @admin.error
    async def admin_error(self, ctx, error):
        """ Error code to be executed when an non-admin attempts to call these commands """
        await ctx.send(embed=discord.Embed(
            title="Missing permissions",
            color=discord.Color(int("fc6f03", 16)),
            description="You do not have permissions to execute this command."
        ))

async def setup(bot):
    await bot.add_cog(Admin(bot))
