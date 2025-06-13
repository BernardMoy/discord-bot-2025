import discord
from discord.ext import commands
from database import *

class TellAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Tell admin messages to the channel that was set up
    @commands.hybrid_command(name="telladmin",
                        description="Tell admins a message. Your message will not be shown to others.")
    async def telladmin(self, ctx, *, message=""):
        # Get the channel id that was set up for admin messaging
        message_channel = db_get_admin_messages_channel(ctx)

        # trim the message
        message = message.strip()

        # If the message channel does not exist, this command cannot be used
        if not message_channel:
            await ctx.send(embed=discord.Embed(
                title="Admin message channel not exist",
                color=discord.Color(int("ff546e", 16)),
                description="Set this up using `-setadminmessagechannel` in the desired channel."
            ))
            return

        # If message is none, reject it
        if not message:
            await ctx.send(embed=discord.Embed(
                title="Message cannot be empty",
                color=discord.Color(int("ff546e", 16)),
                description="Usage: `-telladmin [message]`"
            ))
            return

        # Send the user's message in the message channel
        channel = self.bot.get_channel(message_channel)
        embed = discord.Embed(
            title="New Message",
            description=message,
            color=discord.Color(int("ffe354", 16))
        )
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.display_avatar.url)  # User info in footer
        await channel.send(embed=embed)

        # If the user is using slash command, reply them
        # Else DM them
        if ctx.interaction is not None:  # Check if user is using SLASH COMMAND (APP COMMANDS)
            await ctx.reply("Message sent!", ephemeral=True)

        else:
            # Afterwards, delete the user message
            await ctx.message.delete()

            # Send dm
            await ctx.author.send(embed=discord.Embed(
                title="Message sent to admins",
                description=message,
                color=discord.Color(int("ffe354", 16))
            ))

async def setup(bot):
    await bot.add_cog(TellAdmin(bot))