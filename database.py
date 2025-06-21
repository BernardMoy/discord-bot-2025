import sqlite3
import time

conn = None
cursor = None

# Wrapper to handle the database errors
# Do not handle ctx await send actions here: This file for database only
def db_error_wrapper(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Database error: {e}")
            return None
    return wrapper

class Database:
    def __init__(self, testing):
        self.testing = testing

        # Initialise the connection, and use a in-memory database if testing
        if self.testing:
            self.conn = sqlite3.connect(":memory:")
        else:
            self.conn = sqlite3.connect("discordbot.db")

        # Initialise the cursor
        self.cursor = self.conn.cursor()

        # Create the tables
        self.cursor.execute("""
                   CREATE TABLE IF NOT EXISTS user_wordle
                   (
                       wordle_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_id INTEGER NOT NULL, 
                       word TEXT NOT NULL
                    )
                   """)
        self.cursor.execute("""
                       CREATE TABLE IF NOT EXISTS guild_adminchannel(
                        guild_id INTEGER PRIMARY KEY, 
                        channel_id INTEGER NOT NULL
                        )
                       """)
        self.cursor.execute("""
                       CREATE TABLE IF NOT EXISTS guild_qotdchannel(
                        guild_id INTEGER PRIMARY KEY, 
                        channel_id INTEGER NOT NULL 
                        )
                       """)
        self.cursor.execute("""
                       CREATE TABLE IF NOT EXISTS qotds(
                        qotd_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        question TEXT NOT NULL, 
                        user_id INTEGER NOT NULL, 
                        guild_id INTEGER NOT NULL, 
                        scheduled_time INTEGER NOT NULL, 
                        sent BOOLEAN DEFAULT FALSE
                        )
                       """)
        self.cursor.execute("""
                       CREATE TABLE IF NOT EXISTS guild_qotdpingrole(
                        guild_id INTEGER PRIMARY KEY, 
                        role_id INTEGER NOT NULL 
                        )
                       """)

    # Record user wordle wins in the database
    @db_error_wrapper
    def put_wordle_win(self, ctx, word):
        # Insert the (uid, score) data to user wordle db
        self.cursor.execute("INSERT INTO user_wordle (user_id, word) VALUES (?,?)",
                       (ctx.author.id, word))
        self.conn.commit()

    # Get the wordle leaderboard of users in the same guild, sorted in descending order of wins
    @db_error_wrapper
    def get_wordle_leaderboard(self, ctx):
        # Get a list of user ids in ctx.guild to be supplied to the query
        guild_users = [int(m.id) for m in ctx.guild.members]

        # If the guild has no users, return empty rows
        if not guild_users:
            return []

        placeholders = ['?'] * len(guild_users)
        placeholders = ','.join(placeholders)
        rows = self.cursor.execute(f"""SELECT user_id, COUNT(*) AS count 
                                            FROM user_wordle 
                                            WHERE user_id IN ({placeholders})
                                            GROUP BY user_id 
                                            ORDER BY count DESC""",
                              guild_users).fetchall()
        return rows

    # Set the admin message channel, or update it if already exists
    @db_error_wrapper
    def set_admin_messages_channel(self, ctx):
        # Get the guild and channel id
        guild_id = ctx.guild.id
        channel_id = ctx.channel.id

        self.cursor.execute("""INSERT OR REPLACE INTO guild_adminchannel VALUES (?, ?)""", (guild_id, channel_id))

        self.conn.commit()
        return True

    # Remove the admin message channel
    @db_error_wrapper
    def remove_admin_messages_channel(self, ctx):
        # Get the guild and channel id
        guild_id = ctx.guild.id

        self.cursor.execute("""DELETE
                          FROM guild_adminchannel
                          WHERE guild_id = ?""", (guild_id,))
        self.conn.commit()
        return True

    # Get the admin message channel id given a GUILD ID, or None if it does not exist
    @db_error_wrapper
    def get_admin_messages_channel(self, guild_id):
        rows = self.cursor.execute("""SELECT channel_id
                                 FROM guild_adminchannel
                                 WHERE guild_id = ?""", (guild_id,)).fetchall()
        return rows[0][0] if rows and rows[0] else None

    # Set the qotd message channel, or update it if already exists
    @db_error_wrapper
    def set_qotd_channel(self, ctx):
        # Get the guild and channel id
        guild_id = ctx.guild.id
        channel_id = ctx.channel.id

        # Insert or update data
        self.cursor.execute("""INSERT OR REPLACE INTO guild_qotdchannel VALUES (?, ?)""", (guild_id, channel_id))

        self.conn.commit()
        return True

    # Remove the qotd message channel
    @db_error_wrapper
    def remove_qotd_channel(self, ctx):
        # Get the guild and channel id
        guild_id = ctx.guild.id

        self.cursor.execute("""DELETE
                          FROM guild_qotdchannel
                          WHERE guild_id = ?""", (guild_id,))
        self.conn.commit()
        return True

    # Get the qotd message channel id, or None if it does not exist
    @db_error_wrapper
    def get_qotd_channel(self, ctx):
        guild_id = ctx.guild.id
        rows = self.cursor.execute("""SELECT channel_id
                                 FROM guild_qotdchannel
                                 WHERE guild_id = ?""", (guild_id,)).fetchall()
        return rows[0][0] if rows and rows[0] else None

    # Get the next qotd scheduled time of the current guild
    @db_error_wrapper
    def get_qotd_next_scheduled_time(self, ctx):
        guild_id = ctx.guild.id

        # Get the time of the latest qotd (sent or unsent) from the same guild
        latest_time = self.cursor.execute("""
                                     SELECT COALESCE((SELECT scheduled_time
                                                      FROM qotds
                                                      WHERE guild_id = ?
                                                      ORDER BY scheduled_time DESC LIMIT 1 ), 0)
                                     """, (guild_id,)).fetchone()[0]

        current_time = int(time.time())

        # Return the maximum of (current_time, latest_time+24h)
        # As questions must be at least 24 hours apart
        return max(current_time, latest_time + 86400)

    # Add a new qotd to the database
    @db_error_wrapper
    def put_qotd(self, ctx, question, scheduled_time):
        self.cursor.execute("INSERT INTO qotds (question, user_id, guild_id, scheduled_time) VALUES (?, ?, ?, ?)",
                       (question, ctx.author.id, ctx.guild.id, scheduled_time))
        self.conn.commit()
        return True

    # Fetch all qotd that are scheduled before the current time in the database
    @db_error_wrapper
    def get_unsent_qotds(self):
        current_time = time.time()

        # Inner join: Rows are excluded if the qotd channel is not set in a specific guild
        # They will be included again once the channel is set again
        # Get the qotd question, uid, channel to send, qotd ping role, and the qotd count
        # Left join is used to keep entries for missing qotd ping roles as they are optional
        rows = self.cursor.execute("""SELECT question,
                                        user_id,
                                        channel_id,
                                        role_id,
                                        (SELECT COUNT(*)
                                         FROM qotds q1
                                         WHERE q1.guild_id = q.guild_id
                                           AND q1.scheduled_time <= q.scheduled_time)
                                 FROM qotds q
                                          JOIN guild_qotdchannel qc ON q.guild_id = qc.guild_id
                                          LEFT JOIN guild_qotdpingrole qp ON q.guild_id = qp.guild_id
                                 WHERE sent = FALSE
                                   AND scheduled_time <= ?
                              """, (current_time,)).fetchall()

        # return the rows
        return rows

    # Get all scheduled (Unsent) qotds that are either in the past or in the future
    @db_error_wrapper
    def get_scheduled_qotds(self, ctx):
        guild_id = ctx.guild.id
        rows = self.cursor.execute("""
                              SELECT question, user_id, scheduled_time
                              FROM qotds
                              WHERE sent = FALSE
                                AND guild_id = ?""",
                              (guild_id,)
                              ).fetchall()

        # return the rows
        return rows

    # Update all qotd scheduled before the current time to sent = true
    @db_error_wrapper
    def mark_qotds_as_sent(self):
        current_time = time.time()
        self.cursor.execute("""UPDATE qotds
                          SET sent = TRUE
                          WHERE qotd_id in (SELECT qotd_id
                                            FROM qotds
                                                     JOIN guild_qotdchannel ON qotds.guild_id = guild_qotdchannel.guild_id
                                            WHERE sent = FALSE
                                              AND scheduled_time <= ?)
                       """, (current_time,))

        self.conn.commit()
        return True

    # Set the qotd ping role or update it if already exists
    @db_error_wrapper
    def set_qotd_ping_role(self, ctx, role_id):
        # Get the guild and channel id
        guild_id = ctx.guild.id

        self.cursor.execute("""INSERT OR REPLACE INTO guild_qotdpingrole VALUES (?, ?)""", (guild_id, role_id))

        self.conn.commit()
        return True

    # Remove the qotd ping role
    @db_error_wrapper
    def remove_qotd_ping_role(self, ctx):
        # Get the guild id
        guild_id = ctx.guild.id

        self.cursor.execute("""DELETE
                          FROM guild_qotdpingrole
                          WHERE guild_id = ?""", (guild_id,))
        self.conn.commit()
        return True

