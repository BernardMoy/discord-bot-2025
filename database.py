import sqlite3
import time

conn = sqlite3.connect("discordbot.db")
cursor = conn.cursor()

# Wrapper to handle the database errors
# Do not handle ctx await send actions here: This file for database only
def db_error_wrapper(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    return wrapper

# Initialise the database by creating tables
@db_error_wrapper
def init_db():
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS user_wordle
                   (
                       wordle_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_id INTEGER NOT NULL, 
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
@db_error_wrapper
def db_put_wordle_win(ctx, word):
    # Insert the (uid, score) data to user wordle db
    cursor.execute("INSERT INTO user_wordle (user_id, word) VALUES (?,?)",
                       (ctx.author.id, word))
    conn.commit()

# Get the wordle leaderboard of users in the same guild, sorted in descending order of wins
@db_error_wrapper
def db_get_wordle_leaderboard(ctx):
    # Get a list of user ids in ctx.guild to be supplied to the query
    guild_users = [int(m.id) for m in ctx.guild.members]
    # If the guild has no users, return empty rows
    if not guild_users:
        return []

    placeholders = ['?']*len(guild_users)
    placeholders = ','.join(placeholders)
    rows = cursor.execute(f"""SELECT user_id, COUNT(*) AS count 
                                        FROM user_wordle 
                                        WHERE user_id IN ({placeholders})
                                        GROUP BY user_id 
                                        ORDER BY count DESC""",
                              guild_users).fetchall()
    return rows

# Set the admin message channel, or update it if already exists
@db_error_wrapper
def db_set_admin_messages_channel(ctx):
    # Get the guild and channel id
    guild_id = ctx.guild.id
    channel_id = ctx.channel.id

    cursor.execute("""INSERT OR REPLACE INTO guild_adminchannel VALUES (?, ?)""", (guild_id, channel_id))

    conn.commit()
    return True


# Remove the admin message channel
@db_error_wrapper
def db_remove_admin_messages_channel(ctx):
    # Get the guild and channel id
    guild_id = ctx.guild.id

    cursor.execute("""DELETE FROM guild_adminchannel WHERE guild_id = ?""", (guild_id, ))
    conn.commit()
    return True


# Get the admin message channel id given a GUILD ID, or None if it does not exist
@db_error_wrapper
def db_get_admin_messages_channel(guild_id):
    rows = cursor.execute("""SELECT channel_id FROM guild_adminchannel WHERE guild_id = ?""", (guild_id,)).fetchall()
    return rows[0][0]

# Set the qotd message channel, or update it if already exists
@db_error_wrapper
def db_set_qotd_channel(ctx):
    # Get the guild and channel id
    guild_id = ctx.guild.id
    channel_id = ctx.channel.id

    # Insert or update data
    cursor.execute("""INSERT OR REPLACE INTO guild_qotdchannel VALUES (?, ?)""", (guild_id, channel_id))

    conn.commit()
    return True


# Remove the qotd message channel
@db_error_wrapper
def db_remove_qotd_channel(ctx):
    # Get the guild and channel id
    guild_id = ctx.guild.id

    cursor.execute("""DELETE FROM guild_qotdchannel WHERE guild_id = ?""", (guild_id, ))
    conn.commit()
    return True

# Get the qotd message channel id, or None if it does not exist
@db_error_wrapper
def db_get_qotd_channel(ctx):
    guild_id = ctx.guild.id
    rows = cursor.execute("""SELECT channel_id FROM guild_qotdchannel WHERE guild_id = ?""", (guild_id,)).fetchall()
    return rows[0][0]

# Get the next qotd scheduled time of the current guild
@db_error_wrapper
def db_get_qotd_next_scheduled_time(ctx):
    guild_id = ctx.guild.id

    # Get the time of the latest qotd (sent or unsent) from the same guild
    latest_time = cursor.execute("""
            SELECT COALESCE((
                SELECT scheduled_time FROM qotds 
                WHERE guild_id = ?
                ORDER BY scheduled_time DESC LIMIT 1
            ), 0)
        """, (guild_id,)).fetchone()[0]

    current_time = int(time.time())

    # Return the maximum of (current_time, latest_time+24h)
    # As questions must be at least 24 hours apart
    return max(current_time, latest_time+86400)

# Add a new qotd to the database
@db_error_wrapper
def db_put_qotd(ctx, question, scheduled_time):
    cursor.execute("INSERT INTO qotds (question, user_id, guild_id, scheduled_time) VALUES (?, ?, ?, ?)",
                       (question, ctx.author.id, ctx.guild.id, scheduled_time))
    conn.commit()
    return True

# Fetch all qotd that are scheduled before the current time in the database
@db_error_wrapper
def db_get_unsent_qotds():
    current_time = time.time()

    # Inner join: Rows are excluded if the qotd channel is not set in a specific guild
    # They will be included again once the channel is set again
    rows = cursor.execute("""SELECT question, user_id, channel_id
                                 FROM qotds JOIN guild_qotdchannel ON qotds.guild_id = guild_qotdchannel.guild_id
                                 WHERE sent = FALSE AND scheduled_time <= ?
                              """, (current_time,)).fetchall()

    # return the rows
    return rows


# Update all qotd scheduled before the current time to sent = true
@db_error_wrapper
def db_mark_qotds_as_sent():
    current_time = time.time()
    cursor.execute("""UPDATE qotds 
                            SET sent = TRUE 
                            WHERE qotd_id in (SELECT qotd_id
                                 FROM qotds JOIN guild_qotdchannel ON qotds.guild_id = guild_qotdchannel.guild_id
                                 WHERE sent = FALSE AND scheduled_time <= ?)
                            """, (current_time,))

    conn.commit()
    return True

