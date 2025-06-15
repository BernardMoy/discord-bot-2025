import discord
from discord.ext import commands
from discord.ui import Select, View

from database import *

class TellAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Tell admin messages to the channel that was set up
    @commands.hybrid_command(name="telladmin",
                        description="Tell admins a message via bot DM. Your message will not be shown to others.")
    async def telladmin(self, ctx, *, message=""):
        # Get the current guild
        current_guild = ctx.guild

        # If the current guild is not None, redirect the user to use this command via DM
        if current_guild is not None:
            await ctx.send(embed=discord.Embed(
                title="Please use this command in DM",
                color=discord.Color(int("ff546e", 16)),
                description="Select the server from using `-telladmin` in DM."
            ))
            return

        # Get a list of mutual guilds that the current member is also in
        mutual_guilds = [g for g in self.bot.guilds if g.get_member(ctx.author.id)]

        # Ask the user what server they want to send this to
        select = Select(
            placeholder="Select a server...",
            options = [
                discord.SelectOption(label = g.name, value = g.id) for g in mutual_guilds
            ]
        )

        # Callback function when the user interacts with the dropdown menu
        async def server_select_callback(interaction):
            selected_value = select.values[0]
            await interaction.response.send_message(selected_value)

        # Set callback and send the view to the user
        select.callback = server_select_callback
        view = View()
        view.add_item(select)
        await ctx.send("Which server do you want to send this message to? Your message will be sent to a channel that admins of that server have set up.",
                       view = view)

        # Get the channel id that was set up for admin messaging
        message_channel = db_get_admin_messages_channel(current_guild.id)

        # If the message channel does not exist, this command cannot be used
        if not message_channel:
            await ctx.send(embed=discord.Embed(
                title="Admin message channel not exist",
                color=discord.Color(int("ff546e", 16)),
                description="Set this up using `-setadminmessagechannel` in the desired channel."
            ))
            return

        # trim the message
        message = message.strip()

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

        # Add the author information in footer
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