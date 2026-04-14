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

def get_all_paths():
    return query_db("SELECT * FROM paths")

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

# Snapshot / Branching Functions
def commit_snapshot(session_id, user_input, response, seed, location_id, branch_name='main'):
    """
    Saves a new turn as a snapshot and updates the story head.
    """
    head = get_story_head(session_id)
    parent_id = head['current_snapshot_id'] if head else None
    turn_number = (head['turn_number'] + 1) if head else 1
    
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            """INSERT INTO snapshots 
               (parent_id, session_id, turn_number, branch_name, narrative_seed, user_input, assistant_response, location_id) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (parent_id, session_id, turn_number, branch_name, seed, user_input, response, location_id)
        )
        snapshot_id = cur.lastrowid
        
        conn.execute(
            "INSERT OR REPLACE INTO story_heads (session_id, current_snapshot_id, active_branch) VALUES (?, ?, ?)",
            (session_id, snapshot_id, branch_name)
        )
        conn.commit()
        return snapshot_id

def get_story_head(session_id):
    """
    Returns the current active snapshot info for a session.
    """
    return query_db(
        """SELECT s.* FROM snapshots s 
           JOIN story_heads h ON s.id = h.current_snapshot_id 
           WHERE h.session_id = ?""",
        (session_id,),
        one=True
    )

def get_snapshot_history(session_id, head_id=None):
    """
    Walks up the parent tree from a head ID to get the linear history.
    """
    if not head_id:
        head = get_story_head(session_id)
        if not head: return []
        head_id = head['id']
        
    history = []
    curr_id = head_id
    while curr_id:
        snap = query_db("SELECT * FROM snapshots WHERE id = ?", (curr_id,), one=True)
        if not snap: break
        history.append(snap)
        curr_id = snap['parent_id']
        
    return history[::-1] # Reverse to get chronological order

# Quest System Functions
def add_quest(title, description, priority=1):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "INSERT INTO quests (title, description, priority) VALUES (?, ?, ?)",
            (title, description, priority)
        )
        conn.commit()
        return cur.lastrowid

def add_quest_objective(quest_id, description):
    execute_db(
        "INSERT INTO quest_objectives (quest_id, description) VALUES (?, ?)",
        (quest_id, description)
    )

def get_active_quests():
    quests = query_db("SELECT * FROM quests WHERE status = 'active' ORDER BY priority DESC")
    full_quests = []
    for q in quests:
        q_dict = dict(q)
        q_dict['objectives'] = query_db("SELECT * FROM quest_objectives WHERE quest_id = ? AND status = 'active'", (q['id'],))
        full_quests.append(q_dict)
    return full_quests

def update_quest_status(quest_id, status):
    execute_db("UPDATE quests SET status = ? WHERE id = ?", (status, quest_id))

def update_objective_status(objective_id, status):
    execute_db("UPDATE quest_objectives SET status = ? WHERE id = ?", (status, objective_id))

# Social Layer Functions
def get_relationship(char_a_id, char_b_id):
    # Ensure consistent ordering for lookup
    a, b = min(char_a_id, char_b_id), max(char_a_id, char_b_id)
    result = query_db("SELECT * FROM relationships WHERE char_a_id = ? AND char_b_id = ?", (a, b), one=True)
    if not result:
        return {"trust": 0, "fear": 0, "affection": 0}
    return dict(result)

def update_relationship(char_a_id, char_b_id, delta_trust, delta_fear, delta_affection, event_desc):
    a, b = min(char_a_id, char_b_id), max(char_a_id, char_b_id)
    
    with sqlite3.connect(DB_PATH) as conn:
        # 1. Update or Insert Relationship
        conn.execute("""
            INSERT INTO relationships (char_a_id, char_b_id, trust, fear, affection)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(char_a_id, char_b_id) DO UPDATE SET
                trust = trust + excluded.trust,
                fear = fear + excluded.fear,
                affection = affection + excluded.affection
        """, (a, b, delta_trust, delta_fear, delta_affection))
        
        # 2. Log Interaction
        conn.execute("""
            INSERT INTO interaction_log (char_a_id, char_b_id, event_description, delta_trust, delta_fear, delta_affection)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (char_a_id, char_b_id, event_desc, delta_trust, delta_fear, delta_affection))
        conn.commit()

def get_character_relationships(char_id):
    """Returns all relationships for a specific character, including with the player (id 0)."""
    return query_db("""
        SELECT r.*, c.name as other_name FROM relationships r
        JOIN characters c ON (r.char_a_id = c.id OR r.char_b_id = c.id)
        WHERE (r.char_a_id = ? OR r.char_b_id = ?) AND c.id != ?
        UNION
        SELECT r.*, 'Player' as other_name FROM relationships r
        WHERE (r.char_a_id = ? AND r.char_b_id = 0) OR (r.char_a_id = 0 AND r.char_b_id = ?)
    """, (char_id, char_id, char_id, char_id, char_id))

# Foreshadowing Functions
def add_foreshadowed_element(name, location, impact):
    execute_db(
        "INSERT INTO foreshadowed_elements (element_name, discovery_location, potential_impact) VALUES (?, ?, ?)",
        (name, location, impact)
    )

def get_pending_foreshadowing():
    return query_db("SELECT * FROM foreshadowed_elements WHERE payoff_status = 'pending'")

def resolve_foreshadowing(element_id):
    execute_db("UPDATE foreshadowed_elements SET payoff_status = 'resolved' WHERE id = ?", (element_id,))

if __name__ == "__main__":
    print("Initializing database...")
    init_db()