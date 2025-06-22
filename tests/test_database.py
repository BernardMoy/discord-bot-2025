from unittest.mock import Mock
from database import Database

# Initialise db here
db = Database(testing=True)

def test_put_wordle_win():
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
