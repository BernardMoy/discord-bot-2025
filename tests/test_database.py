from unittest.mock import Mock

import pytest

from database import Database

# Initialise db here - db is the fixture parameter
@pytest.fixture
def db():
    # Create a new database before each test
    test_db = Database(testing=True)

    yield test_db
    test_db.close()

# Test that a wordle win can be inserted into the database
def test_put_wordle_win(db):
    # Create a mocked context object
    mock_ctx = Mock()
    mock_ctx.author.id = "1234567"

    # add the data to database
    db.put_wordle_win(mock_ctx, "word")

    # assert that a single entry of data exist in the db
    cursor = db.get_cursor()
    rows = cursor.execute("""
        SELECT COUNT(*) FROM user_wordle WHERE user_id = ? and word = ? 
                          """, ("1234567", "word")).fetchone()
    assert rows[0] == 1

# Test that a wordle leaderboard return empty when there are no players in the current guild played wordle
def test_get_wordle_leaderboard_empty(db):
    mock_ctx = Mock()
    mock_ctx.guild.members = [Mock(id=1), Mock(id=2), Mock(id=3)]

    # initially, no members have any entry in the user wordle database so there should be no rows
    rows = db.get_wordle_leaderboard(mock_ctx)
    assert len(rows) == 0

# Test that a wordle leaderboard can be returned and ordered by count
def test_get_wordle_leaderboard(db):
    mock_ctx = Mock()
    mock_ctx.guild.members = [Mock(id=1), Mock(id=2), Mock(id=3)]

    # add data to the database initially
    cursor = db.get_cursor()
    cursor.executemany("""
    INSERT INTO user_wordle (user_id, word) VALUES (?, ?)""",
                   [(1, "word"), (2, "word2"), (1, "word3")])
    db.get_conn().commit()

    # Get the wordle leaderboard
    rows = db.get_wordle_leaderboard(mock_ctx)
    assert rows[0] == (1,2)  # First user has 2 wordle wins
    assert rows[1] == (2,1)