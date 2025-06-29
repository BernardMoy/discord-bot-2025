from discord.ext import commands
import discord
import re

emoji_map = {
        0: ":black_large_square:",
        1: ":one:",
        2: ":two:",
        3: ":three:",
        4: ":four:",
        5: ":five:",
        6: ":six:",
        7: ":seven:",
        8: ":eight:",
        9: ":nine:"
    }

# A class to store sudoku board
class Board:
    def __init__(self, board):
        self.board = board

    def get_row(self, x, y):
        return self.board[x]

    def get_col(self, x, y):
        return [self.board[x][y] for x in range(len(self.board))]

    def get_square(self, x, y):
        elements = []
        for h in range(3*(x//3), 3*(x//3)+3):
            for w in range(3*(y//3), 3*(y//3)+3):
                elements.append(self.board[h][w])
        return elements

    # Given a position x,y determine the possible set of numbers there
    def get_available(self, x, y):
        avail = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        banned = self.get_row(x, y).union(self.get_col(x, y)).union(self.get_square(x, y))
        return avail.difference(banned)

    # Method to print the board with a single hint position
    def to_string(self, hint_x, hint_y):
        s = ''
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                if row == hint_x and col == hint_y:
                    s += ':large_orange_diamond:'
                else:
                    s += emoji_map[self.board[row][col]]
            s += '\n'
        return s

class Sudoku(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="hintsudoku", description="Give a hint to a sudoku puzzle for the Discord game. Use 0 for unknowns ", with_app_command=True)
    async def hintsudoku(self, ctx, *, board_str = ''):
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

        # Create the board object
        sudoku_board = Board(board)
        await ctx.send(sudoku_board.to_string(2,3))


async def setup(bot):
    await bot.add_cog(Sudoku(bot))