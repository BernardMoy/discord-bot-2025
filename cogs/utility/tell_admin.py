import discord
from discord.ext import commands
from discord.ui import Select, View
from main import db

class TellAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Tell admin messages to the channel that was set up (Through DM)
    @commands.dm_only()
    @commands.hybrid_command(name="telladmin",
                        description="Tell admins a message via bot DM. Your message will not be shown to others.")
    async def telladmin(self, ctx, *, message=""):
        # If message is none, reject it
        message = message.strip()
        if not message:
            await ctx.send(embed=discord.Embed(
                title="Message cannot be empty",
                color=discord.Color(int("ff546e", 16)),
                description="Usage: `-telladmin [message]`"
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
            # Fetch the selected guild id
            selected_guild_id = select.values[0]

            # Get the admin channel given the guild id
            message_channel = db.get_admin_messages_channel(selected_guild_id)

            # If the message channel does not exist, this command cannot be used
            if not message_channel:
                embed_error=discord.Embed(
                    title="Admin message channel not exist",
                    color=discord.Color(int("ff546e", 16)),
                    description="Set this up using `-setadminmessagechannel` in the desired channel."
                )
                await interaction.response.send_message(embed=embed_error)
                return

            # Else, send the message in the channel
            channel = self.bot.get_channel(message_channel)
            embed = discord.Embed(
                title="New Message",
                description=message,
                color=discord.Color(int("ffe354", 16))
            )

            # Add the author information in footer
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.display_avatar.url)  # User info in footer
            await channel.send(embed=embed)

            # Reply user successful
            await interaction.response.send_message(embed = discord.Embed(
                title="Message sent to admins",
                description=message,
                color=discord.Color(int("ffe354", 16))
            ))

        # Set callback and send the view to the user
        select.callback = server_select_callback
        view = View()
        view.add_item(select)
        await ctx.send("Which server do you want to send this message to? Your message will be sent to a channel that admins of that server have set up.",
                       view = view)

    # Set the admin message channel
    @commands.hybrid_command(name="setadminmessagechannel",
                             description="Set the current channel to be the admin message channel",
                             with_app_command=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setadminmessagechannel(self, ctx):
        result = db.set_admin_messages_channel(ctx)
        if result:
            await ctx.send(embed=discord.Embed(
                title="Admin message channel set",
                color=discord.Color(int("54ff6e", 16)),
                description="Use `-telladmin [message]` to tell messages to admins, which will appear in this channel."
            ))


    # Remove the admin message channel
    @commands.hybrid_command(name="removeadminmessagechannel",
                             description="Remove the admin message channel of the server", with_app_command=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def removeadminmessagechannel(self, ctx):
        result = db.remove_admin_messages_channel(ctx)
        if result:
            await ctx.send(embed=discord.Embed(
                title="Admin message channel removed",
                color=discord.Color(int("ffcc54", 16)),
                description="Users can no longer use `-telladmin` until another channel is set."
            ))


async def setup(bot):
    await bot.add_cog(TellAdmin(bot))