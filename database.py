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
    except Exception as e:
        print(e)

def db_get_wordle_leaderboard():
    # Query the (user, number of wins) pairs from the user wordle db
    # Sorted in descending order of wins
    try:
        rows = cursor.execute("""SELECT user_id, COUNT(*) AS count FROM user_wordle ORDER BY COUNT DESC""").fetchall()
        return rows

    except Exception as e:
        print(e)
    pass

# Set the admin message channel, or update it if already exists
def db_set_admin_messages_channel(ctx):
    # Get the guild and channel id
    guild_id = ctx.guild.id
    channel_id = ctx.channel.id

    try:
        # Check if the guild data already exists
        cursor.execute("""INSERT OR REPLACE INTO guild_adminchannel VALUES (?, ?)""", (guild_id, channel_id))

        conn.commit()

    except Exception as e:
        print(e)