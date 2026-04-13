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

def search_characters(name_fragment):
    return query_db("SELECT * FROM characters WHERE name LIKE ?", (f"%{name_fragment}%",))

def search_lore(topic_fragment):
    return query_db("SELECT * FROM lore WHERE topic LIKE ?", (f"%{topic_fragment}%",))

def get_all_entities():
    chars = query_db("SELECT name FROM characters")
    lore_topics = query_db("SELECT topic FROM lore")
    return [c['name'] for c in chars] + [l['topic'] for l in lore_topics]

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("Initializing database...")
        init_db()
    else:
        print("Database already exists.")