from discord.ext import commands
import discord
import re
import copy

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

    """
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
    """

    # Get the affecting coordinates of rows, cols and square, excluding the (x,y) itself
    def get_affecting_coordinates_row(self, x, y):
        s = set([(x,y) for x in range(len(self.board))])
        s.remove((x,y))
        return s

    def get_affecting_coordinates_col(self, x, y):
        s = set([(x,y) for y in range(len(self.board[0]))])
        s.remove((x,y))
        return s

    def get_affecting_coordinates_square(self, x, y):
        coords = set()
        for h in range(3*(x//3), 3*(x//3)+3):
            for w in range(3*(y//3), 3*(y//3)+3):
                if not (h == x and w == y):
                    coords.add((h,w))

        return coords

    # Given a position x,y return its rows, cols, and square coordinates all at once
    def get_affecting_coordinates(self, x, y):
        coords = set()
        coords |= self.get_affecting_coordinates_row(x,y)
        coords |= self.get_affecting_coordinates_col(x,y)
        coords |= self.get_affecting_coordinates_square(x,y)

        return coords

    # Given a position x,y determine the possible set of numbers there
    # If it already has a non-0 number, its number is the only element in the set
    # Else, the set contains the set of {1-9} minus all elements in the same row, col and square
    def get_available(self, x, y):
        if self.board[x][y] != 0:
            return {self.board[x][y]}

        avail = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        banned = set()
        for coord in self.get_affecting_coordinates(x, y):
            banned.add(self.board[coord[0]][coord[1]])
        return avail.difference(banned)

    # Method to get the next hint of the sudoku puzzle
    # If one grid has available set with length 1, return its coordinate and hint value
    # Else check the affecting coords of its row, col or square. minus the current avail set with them,
    # and after minus if the remaining avail set has length 1, return its coordinate and hint value
    def get_hint(self):
        d = {}
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                # Find the available set of that position
                avail_set = self.get_available(row, col)
                if self.board[row][col] == 0 and len(avail_set) == 1:
                    return (row, col), list(avail_set)[0]

                # Check if the available set has length 1. If yes, return the coordinate and the hint value
                d[(row, col)] = avail_set

        # For each row, col in the dict, minus all the sets from the avail set of the affecting coordinate of it
        for coord, avail_set in d.items():
            row, col = coord

            if self.board[row][col] != 0:
                continue

            # Consider the avail set for each row, col and square of the current coord
            avail_set_copy = avail_set.copy()
            for a_row, a_col in self.get_affecting_coordinates_row(row, col):
                avail_set_copy -= self.get_available(a_row, a_col)

            # After removing, if the set has length 1 remaining, return it
            if len(avail_set_copy) == 1:
                return (row, col), list(avail_set_copy)[0]

            # Repeat for the column
            avail_set_copy = avail_set.copy()
            for a_row, a_col in self.get_affecting_coordinates_col(row, col):
                avail_set_copy -= self.get_available(a_row, a_col)

            # After removing, if the set has length 1 remaining, return it
            if len(avail_set_copy) == 1:
                return (row, col), list(avail_set_copy)[0]

            # Repeat for square
            avail_set_copy = avail_set.copy()
            for a_row, a_col in self.get_affecting_coordinates_square(row, col):
                avail_set_copy -= self.get_available(a_row, a_col)

            # After removing, if the set has length 1 remaining, return it
            if len(avail_set_copy) == 1:
                return (row, col), list(avail_set_copy)[0]

        # Else, no hints found
        return None, 0

    # Method to print the board with a single hint position
    def to_string(self, hint_x, hint_y):
        s = ''
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                if row == hint_x and col == hint_y:
                    s += ':large_orange_diamond:'
                else:
                    s += emoji_map[self.board[row][col]]

                if (col+1) % 3 == 0:
                    s += '    '
            s += '\n'
            if (row+1) % 3 == 0:
                s += '\n'
        return s

    # Debug method to print the available sets for each grid
    def debug(self):
        avail_set_board =copy.deepcopy(self.board)
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                avail_set = self.get_available(row, col)
                avail_set_board[row][col] = avail_set

        s = ""
        for row in avail_set_board:
            s += str(row)
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

        # Get the next hint
        coord, hint_value = sudoku_board.get_hint()

        # if coord is None, no hints are found
        if not coord:
            embed_not_found = discord.Embed(
                title="No hints found :(",
                description=f"Is your input correct? ",
                color=discord.Color(int("f5429e", 16))
            )
            embed_not_found.set_footer(text = "A depth 1 search is too weak for this")
            await ctx.send(embed = embed_not_found)
            return

        # Create the description text for the embed hint
        hint_x, hint_y = coord[0], coord[1]
        description = sudoku_board.to_string(hint_x, hint_y)

        embed_hint = discord.Embed(
            title = "Sudoku hint",
            description=description,
            color=discord.Color(int("5afc03", 16))
        )

        embed_hint.add_field(name = "Answer", value = f'||{emoji_map[hint_value]}||', inline = False)

        # Create the new command for the next iteration
        board[hint_x][hint_y] = hint_value
        new_command = '`' + '-hintsudoku ' + ' '.join([''.join([str(c) for c in row]) for row in board]) + '`'
        embed_hint.add_field(name = "Next command", value = new_command, inline = False)

        # Debug print the avail sets
        # print(sudoku_board.debug())

        await ctx.send(embed = embed_hint)


async def setup(bot):
    await bot.add_cog(Sudoku(bot))