import discord
from discord.ext import commands
import requests
import re

class PokemonHint(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Pokemon loaded")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.content.startswith('www'):
            await message.channel.send("E")

        # Listen to hint messages from poketwo
        if message.content.startswith("The pokémon is "):
            # Extract the hint from the message
            hint = message.content[15:-1].lower()
            hint = hint.replace("\_", ".")  # Replace _ with . for regex matching

            # Iterate over the currently 1025 pokemons using the poke API
            # Filter them by regex matching
            response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=10000")
            data = response.json()

            reply = ""
            for pokemon in data["results"]:
                if re.fullmatch(hint, pokemon["name"].lower()):
                    reply += pokemon["name"] + "\n"

            # Create embed
            embed = discord.Embed(
                title="Pokemon match results",
                description="There are no matching pokemons!" if reply == "" else reply,
                color=discord.Color.yellow() if reply != "" else discord.Color(int("0xeb348f", 16))
            )
            await message.channel.send(embed=embed)

        # Allow listening to message continuously
        await self.bot.process_commands(message)


async def setup(bot):
    await bot.add_cog(PokemonHint(bot))