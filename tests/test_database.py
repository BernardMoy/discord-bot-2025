from unittest.mock import Mock
import time
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

# Test that when there are no previous qotds, the scheduled time is the current time
def test_get_qotd_next_scheduled_time_no_qotds(db):
    mock_ctx = Mock()
    mock_ctx.guild = Mock(id = 618)

    # there are no previous entries of that guild id in the qotd database
    scheduled_time = db.get_qotd_next_scheduled_time(mock_ctx)

    # the time should be close to the current time with 1s difference
    current_time = int(time.time())
    print(current_time)
    assert abs(current_time - scheduled_time) < 1

# Test that when there are previous qotds, the scheduled time is the previous latest qotd + 24 hours
def test_get_qotd_next_scheduled_time_with_qotds(db):
    mock_ctx = Mock()
    mock_ctx.guild = Mock(id = 618)

    # The qotds should queue after the current time
    current_time = time.time()

    # add data using same guild id
    cursor = db.get_cursor()
    cursor.executemany("""
                       INSERT INTO qotds(question, user_id, guild_id, scheduled_time)
                       VALUES (?, ?, ?, ?)""",
                       [("q1", 123, 618, current_time+560), ("q1", 123, 615, current_time+650)])
    db.get_conn().commit()

    # the time should be 560 + 24 hrs
    scheduled_time = db.get_qotd_next_scheduled_time(mock_ctx)
    assert scheduled_time == current_time+560+86400

# Test that get unsent qotds return the list of qotd that can immediately be sent
def test_get_unsent_qotds(db):

    # The qotds should queue after the current time
    current_time = time.time()

    # add data using same guild id
    cursor = db.get_cursor()
    cursor.executemany("""
                       INSERT INTO qotds(question, user_id, guild_id, scheduled_time, sent)
                       VALUES (?, ?, ?, ?, ?)""",
                       [("q1", 123, 618, current_time-500, False),
                        ("q2", 123, 618, current_time+200, False),
                        ("q3", 123, 620, current_time-500, False)]
                       )

    # set the 618 guild to have a valid channel id, 620 guild doesnt
    cursor.execute("""
                       INSERT INTO guild_qotdchannel(guild_id, channel_id)
                       VALUES (?, ?)""",
                       (618, 444))
    db.get_conn().commit()

    # only q1 should be fetched
    # q2 is in the future while q3 does not have a valid channel id
    result = db.get_unsent_qotds()
    assert len(result) == 1
    assert result[0][0] == "q1"
    assert result[0][2] == 444
    assert result[0][3] is None  # No role set
