import discord
from discord.ext import commands, tasks
from discord.ui import Select, View
from main import db

class Qotd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Start the qotd checking loop when on ready
        self.loop.start()

    @commands.guild_only()
    @commands.hybrid_command(name="qotd", description="Ask a question of the day")
    async def qotd(self, ctx, *, question=""):
        # Get the channel id that was set up for admin messaging
        message_channel = db.get_qotd_channel(ctx)

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
        scheduled_time = db.get_qotd_next_scheduled_time(ctx)

        # Add the question to the database
        db.put_qotd(ctx, question, scheduled_time)

        # Reply the user
        embed = discord.Embed(
            title="Question submitted!",
            color=discord.Color(int("54ff6e", 16)),
            description=f"Your question is scheduled on <t:{scheduled_time}>",
        )
        embed.set_footer(text="It may take up to a minute for the question to show up")
        await ctx.send(embed=embed)

    # Loop that executes every minute to check for new, unsent qotds
    @tasks.loop(minutes=1)
    async def loop(self):
        # Print all qotds that are scheduled before the current time
        rows = db.get_unsent_qotds()
        print(f"Checking for new qotds... {len(rows)} new qotds detected")
        print(rows)

        for question, user_id, channel_id, role_id, count in rows:
            embed = discord.Embed(title=f"Question of the day - {count}",
                                  description=question,
                                  color=discord.Color(int("7ee6d4", 16)))

            embed.add_field(name="Asked by", value=f"<@{user_id}>")

            # Get the channel
            channel = await self.bot.fetch_channel(int(channel_id))

            # Ping if there is a qotd ping role
            if role_id:
                await channel.send(f"<@&{role_id}>", embed=embed)
            else:
                await channel.send(embed = embed )

        # After sending, mark all qotds as sent
        db.mark_qotds_as_sent()

    # Set the qotd message channel
    @commands.hybrid_command(name="setqotdchannel",
                                description="Set the current channel to be the qotd message channel",
                                with_app_command=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setqotdchannel(self, ctx):
        result = db.set_qotd_channel(ctx)
        if result:
            await ctx.send(embed=discord.Embed(
                title="QOTD channel set",
                color=discord.Color(int("54ff6e", 16)),
                description="Use `-qotd [question]` to ask QOTDs, which will appear in this channel."
            ))

    # Remove the qotd message channel
    @commands.hybrid_command(name="removeqotdchannel", description="Remove the qotd message channel of the server",
                                 with_app_command=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def removeqotdchannel(self, ctx):
        result = db.remove_qotd_channel(ctx)
        if result:
            await ctx.send(embed=discord.Embed(
                title="QOTD channel removed",
                color=discord.Color(int("ffcc54", 16)),
                description="Users can no longer use `-qotd` until another channel is set."
            ))

    # Set the qotd ping role
    @commands.hybrid_command(name="setqotdpingrole", description="Set a role to ping for new qotds",
                                         with_app_command=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setqotdpingrole(self, ctx):
        # Get a list of roles of the current guild
        roles = ctx.guild.roles

        select = Select(
                        placeholder="Select a role...",
                        options=[
                            discord.SelectOption(label=r.name, value=r.id) for r in roles
                        ]
        )

        async def role_select_callback(interaction):
            selected_role_id = select.values[0]

            # Update the role in database
            db.set_qotd_ping_role(ctx, selected_role_id)
            await interaction.response.send_message("Qotd ping role set!")

        select.callback = role_select_callback

        # Create new view to send the select screen
        view = View()
        view.add_item(select)
        await ctx.send("Select a ping role for QOTD", view=view)

    # Remove the qotd ping role
    @commands.hybrid_command(name="removeqotdpingrole", description="Remove the qotd ping role",
                                         with_app_command=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def removeqotdpingrole(self, ctx):
        result = db.remove_qotd_ping_role(ctx)
        if result:
            await ctx.send(embed=discord.Embed(
                title="QOTD ping role removed",
                color=discord.Color(int("ffcc54", 16)),
                description="No users will be pinged for new questions."
            ))

    # Show a list of scheduled qotds
    @commands.hybrid_command(name="scheduledqotds", description="Get all scheduled qotds",
                                         with_app_command=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def scheduledqotds(self, ctx):
        rows = db.get_scheduled_qotds(ctx)
        content = "" if rows else "There are no scheduled qotds in this server."
        for question, user_id, scheduled_time in rows:
            content += question + "\n"
            content += f"Sent by: <@{user_id}>\n"
            content += f"Scheduled on: <t:{scheduled_time}>\n\n"

        await ctx.send(
            embed=discord.Embed(
            title="Scheduled QOTDs",
            color=discord.Color(int("f5e342", 16)),
            description=content
        ))

async def setup(bot):
    await bot.add_cog(Qotd(bot))