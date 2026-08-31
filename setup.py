import sqlite3

with sqlite3.connect("alterDB.db") as conn:
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Alters (
            alter_id INTEGER PRIMARY KEY,
            Name TEXT,
            Pronouns TEXT,
            Role TEXT,
            Image_URL TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SystemStatus (
            ID INTEGER PRIMARY KEY,
            CurrentFronter TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CoreInfo (
            host_id INTEGER
        )
    """)
