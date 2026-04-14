import sqlite3
import os
import memory_engine

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
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("INSERT INTO characters (name, description, traits, voice_id) VALUES (?, ?, ?, ?)", 
                        (name, description, traits, voice_id))
        conn.commit()
        char_id = cur.lastrowid
        memory_engine.add_character_vector(name, description, traits, char_id)

def add_lore(topic, description):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("INSERT INTO lore (topic, description) VALUES (?, ?)", (topic, description))
        conn.commit()
        lore_id = cur.lastrowid
        memory_engine.add_lore_vector(topic, description, lore_id)

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

def log_history(user_input, assistant_response):
    execute_db("INSERT INTO history (user_input, assistant_response) VALUES (?, ?)", 
               (user_input, assistant_response))

def get_recent_history(limit=10):
    return query_db("SELECT user_input, assistant_response FROM history ORDER BY id DESC LIMIT ?", (limit,))

def get_history_count():
    result = query_db("SELECT COUNT(*) as count FROM history", one=True)
    return result['count']

def set_story_state(key, value):
    execute_db("INSERT OR REPLACE INTO story_state (key, value) VALUES (?, ?)", (key, value))

def get_story_state(key):
    result = query_db("SELECT value FROM story_state WHERE key = ?", (key,), one=True)
    return result['value'] if result else None

# World Map Functions
def add_location(name, description, x, y, biome_type, region_id=None):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "INSERT INTO locations (name, description, x, y, biome_type, region_id) VALUES (?, ?, ?, ?, ?, ?)",
            (name, description, x, y, biome_type, region_id)
        )
        conn.commit()
        return cur.lastrowid

def get_location(location_id):
    return query_db("SELECT * FROM locations WHERE id = ?", (location_id,), one=True)

def get_location_by_name(name):
    return query_db("SELECT * FROM locations WHERE name = ?", (name,), one=True)

def get_all_locations():
    return query_db("SELECT * FROM locations")

def set_entity_position(entity_type, entity_id, location_id):
    execute_db(
        "INSERT OR REPLACE INTO entity_positions (entity_type, entity_id, current_location_id) VALUES (?, ?, ?)",
        (entity_type, entity_id, location_id)
    )

def get_entity_position(entity_type, entity_id):
    return query_db(
        "SELECT * FROM entity_positions WHERE entity_type = ? AND entity_id = ?",
        (entity_type, entity_id),
        one=True
    )

if __name__ == "__main__":
    print("Initializing database...")
    init_db()