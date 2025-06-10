import sqlite3

conn = sqlite3.connect("discordbot.db")
cursor = conn.cursor()

# Initialise the database by creating tables
def init_db():
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS user_wordle
                   (
                       user_id INTEGER PRIMARY KEY, 
                       word TEXT NOT NULL
                    )
                   """)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS guild_adminchannel(
                    guild_id INTEGER PRIMARY KEY, 
                    channel_id INTEGER NOT NULL 
                    )
                   """)


def db_put_wordle_win(ctx, word):
    # Insert the (uid, score) data to user wordle db
    try:
        cursor.execute("INSERT INTO user_wordle VALUES (?, ?)",
                       (ctx.author.id, word))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False

def db_get_wordle_leaderboard():
    # Query the (user, number of wins) pairs from the user wordle db
    # Sorted in descending order of wins
    try:
        rows = cursor.execute("""SELECT user_id, COUNT(*) AS count FROM user_wordle ORDER BY COUNT DESC""").fetchall()
        return rows

    except Exception as e:
        print(e)

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