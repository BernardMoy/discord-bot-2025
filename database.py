import sqlite3

conn = sqlite3.connect("discordbot.db")
cursor = conn.cursor()

# Initialise the database by creating tables
def init_db():
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users
                   (
                       user_id CHAR(255) PRIMARY KEY,
                       user_name TEXT NOT NULL
                    )
                   """)