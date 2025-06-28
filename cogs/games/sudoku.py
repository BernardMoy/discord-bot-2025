from discord.ext import commands
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

        for row in re.split(r' |\n', board_str):
            cur_row = [int(s) for s in list(row)]
            if cur_row:
                board.append(cur_row)

        await ctx.send(board)

async def setup(bot):
    await bot.add_cog(Sudoku(bot))