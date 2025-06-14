import sqlite3
import time

conn = sqlite3.connect("discordbot.db")
cursor = conn.cursor()

# Initialise the database by creating tables
def init_db():
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS user_wordle
                   (
                       wordle_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_id INTEGER NOT NULL, 
                       guild_id INTEGER NOT NULL, 
                       word TEXT NOT NULL
                    )
                   """)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS guild_adminchannel(
                    guild_id INTEGER PRIMARY KEY, 
                    channel_id INTEGER NOT NULL 
                    )
                   """)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS guild_qotdchannel(
                    guild_id INTEGER PRIMARY KEY, 
                    channel_id INTEGER NOT NULL 
                    )
                   """)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS qotds(
                    qotd_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    question TEXT NOT NULL, 
                    user_id INTEGER NOT NULL, 
                    guild_id INTEGER NOT NULL, 
                    scheduled_time INTEGER NOT NULL, 
                    sent BOOLEAN DEFAULT FALSE
                    )
                   """)


# Record user wordle wins in the database
def db_put_wordle_win(ctx, word):
    # Insert the (uid, score) data to user wordle db
    try:
        cursor.execute("INSERT INTO user_wordle (user_id, guild_id, word) VALUES (?, ?, ?)",
                       (ctx.author.id, ctx.guild.id, word))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False

# Get the wordle leaderboard of users in the same guild
def db_get_wordle_leaderboard(ctx):
    # Query the (user, number of wins) pairs from the user wordle db
    # Sorted in descending order of wins
    try:
        rows = cursor.execute("""SELECT user_id, COUNT(*) AS count FROM user_wordle WHERE guild_id = ? ORDER BY COUNT DESC""", (ctx.guild.id,)).fetchall()
        return rows

    except Exception as e:
        print(e)
        return None

# Set the admin message channel, or update it if already exists
def db_set_admin_messages_channel(ctx):
    # Get the guild and channel id
    guild_id = ctx.guild.id
    channel_id = ctx.channel.id

    try:
        # Insert or update data
        cursor.execute("""INSERT OR REPLACE INTO guild_adminchannel VALUES (?, ?)""", (guild_id, channel_id))

        conn.commit()
        return True

    except Exception as e:
        print(e)
        return False

# Remove the admin message channel
def db_remove_admin_messages_channel(ctx):
    # Get the guild and channel id
    guild_id = ctx.guild.id
    try:
        cursor.execute("""DELETE FROM guild_adminchannel WHERE guild_id = ?""", (guild_id, ))
        conn.commit()
        return True

    except Exception as e:
        print(e)
        return False

# Get the admin message channel id, or None if it does not exist
def db_get_admin_messages_channel(ctx):
    guild_id = ctx.guild.id
    try:
        rows = cursor.execute("""SELECT channel_id FROM guild_adminchannel WHERE guild_id = ?""", (guild_id,)).fetchall()
        return rows[0][0]
    except Exception as e:
        print(e)
        return None

# Set the qotd message channel, or update it if already exists
def db_set_qotd_channel(ctx):
    # Get the guild and channel id
    guild_id = ctx.guild.id
    channel_id = ctx.channel.id

    try:
        # Insert or update data
        cursor.execute("""INSERT OR REPLACE INTO guild_qotdchannel VALUES (?, ?)""", (guild_id, channel_id))

        conn.commit()
        return True

    except Exception as e:
        print(e)
        return False

# Remove the qotd message channel
def db_remove_qotd_channel(ctx):
    # Get the guild and channel id
    guild_id = ctx.guild.id
    try:
        cursor.execute("""DELETE FROM guild_qotdchannel WHERE guild_id = ?""", (guild_id, ))
        conn.commit()
        return True

    except Exception as e:
        print(e)
        return False

# Get the qotd message channel id, or None if it does not exist
def db_get_qotd_channel(ctx):
    guild_id = ctx.guild.id
    try:
        rows = cursor.execute("""SELECT channel_id FROM guild_qotdchannel WHERE guild_id = ?""", (guild_id,)).fetchall()
        return rows[0][0]
    except Exception as e:
        print(e)
        return None

# Get the next qotd scheduled time of the current guild
def db_get_qotd_next_scheduled_time(ctx):
    guild_id = ctx.guild.id
    try:
        # Get the time of the latest unsent qotd from the same guild
        latest_time = cursor.execute("""
            SELECT COALESCE((
                SELECT scheduled_time FROM qotds 
                WHERE guild_id = ? AND sent = FALSE 
                ORDER BY scheduled_time DESC LIMIT 1
            ), 0)
        """, (guild_id,)).fetchone()[0]

        current_time = int(time.time())

        # Return the maximum of (current_time, latest_time+24h)
        # As questions must be at least 24 hours apart
        return max(current_time, latest_time+86400)

    except Exception as e:
        print(e)
        return None

