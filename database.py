import sqlite3

conn = sqlite3.connect("discordbot.db")
cursor = conn.cursor()

# Initialise the database by creating tables
def init_db():
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS user_wordle
                   (
                       user_id INTEGER, 
                       word TEXT, 
                       FOREIGN KEY (user_id) REFERENCES users(user_id)
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

def db_get_wordle_leaderboard(ctx):
    pass