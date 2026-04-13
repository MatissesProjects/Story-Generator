import sqlite3
import os

DB_PATH = "story_memory.db"

def init_db():
    with open("schema.sql", "r") as f:
        schema = f.read()
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(schema)

def query_db(query, args=(), one=False):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, args)
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(query, args)
        conn.commit()

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("Initializing database...")
        init_db()
    else:
        print("Database already exists.")