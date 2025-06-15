import discord
from discord.ext import commands
import random
from data.wordle_list import wordle_list
from database import *


# Function to return a random, 5 letter word
def get_random_five_letter_word():
    word = random.choice(list(wordle_list))

    # Print the word
    print(f"New wordle round started: {word}")
    return word


class Wordle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Store additional class variables for wordle game
        self.current_wordle_word = ""    # Current 5 letter word
        self.current_wordle_result = ""  # Current wordle result to be printed
        self.current_wordle_tries = 0    # Current number of tries
        self.current_wordle_dict = set() # Current used letters


    # Function to reset class variables for wordle, but does not generate a new 5 letter word
    def reset_wordle(self):
        self.current_wordle_word = ""
        self.current_wordle_result = ""
        self.current_wordle_tries = 0
        self.current_wordle_dict.clear()

    # Get the keyboard to be added to the wordle result last
    def get_keyboard(self):
        keyboard = ""
        for char in "qwertyuiop":
            keyboard += f":regional_indicator_{char}: " if char not in self.current_wordle_dict else ":black_large_square: "
        keyboard += '\n    '

        for char in "asdfghjkl":
            keyboard += f":regional_indicator_{char}: " if char not in self.current_wordle_dict else ":black_large_square: "
        keyboard += '\n        '

        for char in "zxcvbnm":
            keyboard += f":regional_indicator_{char}: " if char not in self.current_wordle_dict else ":black_large_square: "
        keyboard += '\n'

        return keyboard

    @commands.hybrid_command(name = "wordle", description = "Play 5-letter wordle", with_app_command=True)
    async def wordle(self, ctx, guess=""):
        # Trim the guess
        guess = guess.lower().strip()

        # If guess is not provided, send usage message
        if guess == '':
            embed = discord.Embed(
                title="Usage",
                description=f"`-wordle [guess]` or \n `-wordle -reset` to reset",
                color=discord.Color(int("f5429e", 16))
            )
            await ctx.send(embed=embed)
            return


        # If guess is "-reset", reset it
        if guess == "-reset":
            self.reset_wordle()
            self.current_wordle_word = get_random_five_letter_word()

            embed = discord.Embed(
                title=f"Wordle has been reset",
                description="Use -wordle `xxxxx` for your first guess",
                color=discord.Color(int("42b0f5", 16))
            )

            await ctx.send(embed=embed)
            return


        if len(guess) != 5 or guess not in wordle_list:
            # If the guess has incorrect length or is not a valid word, warn the user
            embed = discord.Embed(
                title="Invalid guess",
                description=f"`{guess}` is not a 5 letter word. \n\n {self.get_keyboard()}",
                color=discord.Color(int("f5429e", 16))
            )

            # Set the footer by including the keyboard and the reset warning
            embed.set_footer(text="Use -wordle -reset to reset the game")
            await ctx.send(embed=embed)
            return

        # If the current wordle word is empty, get a new random five letter word
        if self.current_wordle_word == "":
            self.current_wordle_word = get_random_five_letter_word()

        # Iterate over every position of the guessed (5 letter) word
        word_emojis = "".join([f":regional_indicator_{x}:" for x in guess])
        result = ""
        for i in range(5):
            if self.current_wordle_word[i] == guess[i]:
                result += ":green_square:"
            elif guess[i] in list(self.current_wordle_word):
                result += ":yellow_square:"
            else:
                result += ":black_large_square:"

                # Add the used character to the dict
                self.current_wordle_dict.add(guess[i])

        # Append to the global wordle result
        self.current_wordle_result += f"\n {word_emojis} \n{result} \n"

        # Add the tries
        self.current_wordle_tries += 1

        embed = discord.Embed(
            title=f"Wordle {self.current_wordle_tries}/6",
            description=f"{self.current_wordle_result} \n\n {self.get_keyboard()}",
            color=discord.Color(int("42b0f5", 16))
        )

        embed.set_footer(text="Use -wordle -reset to reset the game")
        await ctx.send(embed=embed)

        # If the guess is correct, send message
        if guess == self.current_wordle_word:
            await ctx.send(embed=discord.Embed(
                title=f"You won!",
                description=ctx.author.mention,
                color=discord.Color(int("93f542", 16))
            ))

            # Add to database
            db_put_wordle_win(ctx, self.current_wordle_word)

            # Reset the wordle for the next round
            self.reset_wordle()

        # If the number of tries is 6, end the game
        elif self.current_wordle_tries == 6:
            await ctx.send(embed=discord.Embed(
                title=f"You lost!",
                description=f"The word was `{self.current_wordle_word}`.",
                color=discord.Color(int("f57b42", 16))
            ))

            self.reset_wordle()


async def setup(bot):
    await bot.add_cog(Wordle(bot))