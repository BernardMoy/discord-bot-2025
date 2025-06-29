from discord.ext import commands
import discord
import re

class Sudoku(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="hintsudoku", description="Give a hint to a sudoku puzzle for the Discord game. Use 0 for unknowns ", with_app_command=True)
    async def hintsudoku(self, ctx, *, board_str):
        # Trim the board
        board_str = board_str.strip()

        # Create the board from the string provided
        board = []

        # Load into board and check for correct format
        embed_error = discord.Embed(
                title="Usage",
                description=f"`-hintsudoku 000005702 090700030...`",
                color=discord.Color(int("f5429e", 16))
            )
        embed_error.set_footer(text = "Use 0 for the unknowns.")

        for row in re.split(r' |\n', board_str):
            cur_row = [int(s) for s in list(row)]

            if cur_row and len(cur_row) != 9:
                await ctx.send(embed=embed_error)
                return

            if cur_row:
                board.append(cur_row)

        if len(board) != 9:
            await ctx.send(embed=embed_error)
            return

        await ctx.send(board)

async def setup(bot):
    await bot.add_cog(Sudoku(bot))