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

def get_character_voice(name):
    result = query_db("SELECT voice_id FROM characters WHERE name = ?", (name,), one=True)
    return result['voice_id'] if result and result['voice_id'] else "en_US-lessac-medium.onnx" # Default voice

def add_character(name, description, traits, voice_id="en_US-lessac-medium.onnx"):
    execute_db("INSERT INTO characters (name, description, traits, voice_id) VALUES (?, ?, ?, ?)", 
               (name, description, traits, voice_id))

def add_lore(topic, description):
    execute_db("INSERT INTO lore (topic, description) VALUES (?, ?)", (topic, description))

def add_meta_lore(topic, description, keywords):
    execute_db("INSERT INTO meta_lore (topic, description, keywords) VALUES (?, ?, ?)", 
               (topic, description, keywords))

def get_all_meta_lore():
    return query_db("SELECT * FROM meta_lore")

def get_active_plot_threads():
    return query_db("SELECT description FROM plot_threads WHERE status = 'active'")

def add_plot_thread(description):
    execute_db("INSERT INTO plot_threads (description) VALUES (?)", (description,))

def log_event(description):
    execute_db("INSERT INTO timeline (event_description) VALUES (?)", (description,))

def get_recent_timeline(limit=5):
    return query_db("SELECT event_description FROM timeline ORDER BY id DESC LIMIT ?", (limit,))

if __name__ == "__main__":
    print("Initializing database...")
    init_db()