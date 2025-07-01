"""
Tests for the Board class in the hint_sudoku method.
"""
import pytest
from cogs.games.sudoku import Board

@pytest.fixture
def board():
     # Create a new database before each test
     test_board = Board(board = [[0, 0, 0, 0, 0, 0, 8, 9, 0],
                                 [6, 0, 0, 7, 0, 8, 0, 0, 0],
                                 [8, 2, 1, 0, 0, 0, 0, 0, 5],
                                 [0, 0, 6, 0, 0, 5, 0, 0, 0],
                                 [1, 0, 2, 0, 6, 0, 0, 0, 3],
                                 [0, 4, 0, 0, 0, 0, 0, 7, 0],
                                 [0, 0, 5, 4, 3, 2, 0, 0, 0],
                                 [0, 0, 0, 0, 8, 0, 9, 0, 0],
                                 [0, 3, 0, 0, 0, 0, 4, 0, 0]])

     yield test_board


def test_get_affecting_coordinates_row(test_board):
    pass