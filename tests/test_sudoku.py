"""
Tests for the Board class in the hint_sudoku method.
"""
import pytest
from cogs.games.sudoku import Board

@pytest.fixture
def test_board():
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
    rows = test_board.get_affecting_coordinates_row(2,3)
    assert rows == {(2,0), (2,1), (2,2), (2,4), (2,5), (2,6), (2,7), (2,8)}

def test_get_affecting_coordinates_col(test_board):
    col = test_board.get_affecting_coordinates_col(2,3)
    assert col == {(0,3), (1,3), (3,3), (4,3), (5,3), (6,3), (7,3), (8,3)}

def test_get_affecting_coordinates_square(test_board):
    sq = test_board.get_affecting_coordinates_square(2,3)
    assert sq == {(0,3), (0,4), (0,5), (1,3), (1,4), (1,5), (2,4), (2,5)}

def test_get_available(test_board):
    avail_set = test_board.get_available(0,5)
    assert avail_set == {1,3,4,6}

def get_next_hint_avail_set_length_one():
    test_board = Board(board=[[0, 0, 0, 0, 0, 0, 8, 9, 0],
                              [6, 9, 4, 7, 5, 8, 3, 0, 1],
                              [8, 2, 1, 0, 0, 0, 0, 0, 5],
                              [0, 0, 6, 0, 0, 5, 0, 0, 0],
                              [1, 0, 2, 0, 6, 0, 0, 0, 3],
                              [0, 4, 0, 0, 0, 0, 0, 7, 0],
                              [0, 0, 5, 4, 3, 2, 0, 0, 0],
                              [0, 0, 0, 0, 8, 0, 9, 0, 0],
                              [0, 3, 0, 0, 0, 0, 4, 0, 0]])

    coords, hint = test_board.get_hint()
    assert coords == (1,7)
    assert hint == 2

def get_next_hint_avail_set_minus():
    test_board = Board(board=[[0, 0, 0, 1, 0, 6, 0, 0, 0],
                              [0, 0, 6, 4, 0, 3, 0, 0, 0],
                              [0, 0, 0, 0, 7, 0, 3, 0, 0],
                              [6, 3, 0, 7, 9, 0, 8, 2, 0],
                              [8, 0, 0, 6, 0, 5, 0, 0, 0],
                              [0, 0, 0, 8, 3, 0, 0, 0, 1],
                              [0, 1, 0, 0, 0, 0, 0, 5, 8],
                              [0, 9, 0, 0, 0, 0, 0, 7, 0],
                              [0, 0, 0, 0, 0, 0, 9, 0, 0]])

    coords, hint = test_board.get_hint()
    assert coords == (8, 1)
    assert hint == 6