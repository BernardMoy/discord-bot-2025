import discord
from discord.ext import commands
import re
from pokemon_matcher import pokemon_matcher

class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # Listen to hint messages from poketwo
        if re.match(r"The pok.mon is .+", message.content):
            # Extract the hint from the message
            hint = message.content[15:-1].lower()
            matching_pokemons = pokemon_matcher(hint)
            reply = '\n'.join(matching_pokemons)

            # Create embed
            embed = discord.Embed(
                title="Pokemon match results",
                description="There are no matching pokemons!" if reply == "" else reply,
                color=discord.Color.yellow() if reply != "" else discord.Color(int("0xeb348f", 16))
            )
            await message.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(OnMessage(bot))