import sqlite3
import os
import memory_engine
import config
import json
import random
import threading

DB_PATH = "story_memory.db"
_local = threading.local()

def get_db():
    if not hasattr(_local, "conn") or _local.conn is None:
        _local.conn = sqlite3.connect(DB_PATH, timeout=10.0)
        _local.conn.row_factory = sqlite3.Row
    return _local.conn

def close_db():
    if hasattr(_local, "conn") and _local.conn is not None:
        _local.conn.close()
        _local.conn = None

def init_db():
    with open("schema.sql", "r") as f:
        schema = f.read()
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(schema)
        
        # Simple migration for 'locations' table
        cursor = conn.execute("PRAGMA table_info(locations)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'elevation' not in columns:
            print("Migrating database: Adding 'elevation' to 'locations'")
            conn.execute("ALTER TABLE locations ADD COLUMN elevation INTEGER DEFAULT 0")
            
        if 'climate' not in columns:
            print("Migrating database: Adding 'climate' to 'locations'")
            conn.execute("ALTER TABLE locations ADD COLUMN climate TEXT DEFAULT 'Temperate'")
        
        # Add UNIQUE index for (x, y) if it doesn't exist
        try:
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_locations_coords ON locations(x, y)")
        except sqlite3.OperationalError:
            # Table might already have the constraint or index
            pass
        
        # Simple migration for 'characters' table
        cursor = conn.execute("PRAGMA table_info(characters)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'length_scale' not in columns:
            print("Migrating database: Adding voice modification columns to 'characters'")
            conn.execute("ALTER TABLE characters ADD COLUMN length_scale REAL DEFAULT 1.0")
            conn.execute("ALTER TABLE characters ADD COLUMN noise_scale REAL DEFAULT 0.667")
            conn.execute("ALTER TABLE characters ADD COLUMN noise_w REAL DEFAULT 0.8")
        
        if 'social' not in columns:
            print("Migrating database: Adding motivation columns to 'characters'")
            conn.execute("ALTER TABLE characters ADD COLUMN social INTEGER DEFAULT 50")
            conn.execute("ALTER TABLE characters ADD COLUMN ambition INTEGER DEFAULT 50")
            conn.execute("ALTER TABLE characters ADD COLUMN safety INTEGER DEFAULT 50")
            conn.execute("ALTER TABLE characters ADD COLUMN resources INTEGER DEFAULT 50")
            conn.execute("ALTER TABLE characters ADD COLUMN current_goal TEXT")
            conn.execute("ALTER TABLE characters ADD COLUMN current_task TEXT")
        
        if 'signature_tic' not in columns:
            print("Migrating database: Adding cinematic columns to 'characters'")
            conn.execute("ALTER TABLE characters ADD COLUMN signature_tic TEXT")
            conn.execute("ALTER TABLE characters ADD COLUMN narrative_role TEXT DEFAULT 'NPC'")
            conn.execute("ALTER TABLE characters ADD COLUMN last_seen_turn INTEGER DEFAULT 0")
        
        if 'leitmotif_path' not in columns:
            print("Migrating database: Adding 'leitmotif_path' to 'characters'")
            conn.execute("ALTER TABLE characters ADD COLUMN leitmotif_path TEXT")
        
        # Simple migration for 'relationships' table
        cursor = conn.execute("PRAGMA table_info(relationships)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'base_affection' not in columns:
            print("Migrating database: Adding base anchor columns to 'relationships'")
            conn.execute("ALTER TABLE relationships ADD COLUMN base_trust INTEGER DEFAULT 0")
            conn.execute("ALTER TABLE relationships ADD COLUMN base_fear INTEGER DEFAULT 0")
            conn.execute("ALTER TABLE relationships ADD COLUMN base_affection INTEGER DEFAULT 0")

        conn.commit()

    # Initialize default state if missing
    if get_story_state("narrative_seed") is None:
        set_story_state("narrative_seed", "The story has just begun.")

def query_db(query, args=(), one=False):
    try:
        conn = get_db()
        cur = conn.execute(query, args)
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv
    except sqlite3.Error as e:
        print(f"Database Query Error: {e} (Query: {query})")
        return None if one else []

def execute_db(query, args=()):
    try:
        conn = get_db()
        conn.execute(query, args)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database Execution Error: {e} (Query: {query})")

def clear_all_data():
    tables = [
        "characters", "lore", "plot_threads", "timeline", "meta_lore", 
        "history", "story_state", "regions", "locations", "paths", 
        "entity_positions", "snapshots", "story_heads", "quests", 
        "quest_objectives", "relationships", "interaction_log", 
        "foreshadowed_elements", "inventory", "entity_stats", 
        "simulation_history"
    ]
    conn = get_db()
    for table in tables:
        try:
            conn.execute(f"DELETE FROM {table}")
        except sqlite3.OperationalError:
            # Table might not exist yet
            pass
    conn.commit()
    # Re-initialize just in case some defaults are needed
    init_db()

def search_characters(name_fragment):
    return query_db("SELECT * FROM characters WHERE name LIKE ?", (f"%{name_fragment}%",))

def get_all_characters():
    return query_db("SELECT * FROM characters")

def update_character_needs(char_id, social, ambition, safety, resources, goal=None, task=None):
    execute_db("""
        UPDATE characters 
        SET social = ?, ambition = ?, safety = ?, resources = ?, current_goal = ?, current_task = ?
        WHERE id = ?
    """, (social, ambition, safety, resources, goal, task, char_id))

def search_lore(topic_fragment):
    return query_db("SELECT * FROM lore WHERE topic LIKE ?", (f"%{topic_fragment}%",))

def get_all_entities():
    chars = query_db("SELECT name FROM characters")
    lore_topics = query_db("SELECT topic FROM lore")
    return [c['name'] for c in chars] + [l['topic'] for l in lore_topics]

def get_character_voice(name):
    name = name.strip()
    if name.lower() == "narrator":
        return {
            "voice_id": config.NARRATOR_VOICE,
            "length_scale": 1.0,
            "noise_scale": 0.667,
            "noise_w": 0.8
        }

    # 1. Try exact case-insensitive match
    result = query_db("SELECT name, voice_id, length_scale, noise_scale, noise_w FROM characters WHERE name = ? COLLATE NOCASE", (name,), one=True)
    
    # 2. Try partial match if no exact match
    if not result:
        result = query_db("SELECT name, voice_id, length_scale, noise_scale, noise_w FROM characters WHERE name LIKE ? COLLATE NOCASE", (f"%{name}%",), one=True)
    
    if result:
        v_id = result['voice_id'] or config.DEFAULT_VOICE
        print(f"TTS Match (DB): Speaker '{name}' (matched as '{result['name']}') using {v_id}")
        return {
            "voice_id": v_id,
            "length_scale": result['length_scale'],
            "noise_scale": result['noise_scale'],
            "noise_w": result['noise_w']
        }
    
    # Fallback to a random character voice for completely unknown speakers (NEVER the narrator)
    fallback_voice = random.choice(config.MALE_VOICES + config.FEMALE_VOICES)
    print(f"TTS Match (Fallback): Speaker '{name}' NOT FOUND IN DB. Using random character voice: {fallback_voice}")
    return {
        "voice_id": fallback_voice,
        "length_scale": 1.0,
        "noise_scale": 0.667,
        "noise_w": 0.8
    }

def add_character(name, description, traits, voice_id=None, length_scale=1.0, noise_scale=0.667, noise_w=0.8, signature_tic=None, narrative_role='NPC', leitmotif_path=None):
    if voice_id is None:
        # Simple heuristic to infer gender
        text_to_check = f" {name} {description} {traits} ".lower()
        male_keywords = [" he ", " him ", " his ", " man ", " boy ", " male ", " king ", " prince ", " lord ", " sir "]
        female_keywords = [" she ", " her ", " hers ", " woman ", " girl ", " female ", " queen ", " princess ", " lady ", " madam "]
        
        is_male = any(kw in text_to_check for kw in male_keywords)
        is_female = any(kw in text_to_check for kw in female_keywords)
        
        if is_female and not is_male:
            voice_id = random.choice(config.FEMALE_VOICES)
            print(f"DB: Auto-assigned FEMALE voice to {name}: {voice_id}")
        elif is_male and not is_female:
            voice_id = random.choice(config.MALE_VOICES)
            print(f"DB: Auto-assigned MALE voice to {name}: {voice_id}")
        else:
            # Fallback to completely random if ambiguous, filtering out narrator
            char_voices = [v for v in config.MALE_VOICES + config.FEMALE_VOICES if v != config.NARRATOR_VOICE]
            voice_id = random.choice(char_voices)
            print(f"DB: Ambiguous gender for {name}, assigned random voice: {voice_id}")
        
    # Ensure voice_id has extension
    if voice_id and not voice_id.endswith(".onnx"):
        voice_id += ".onnx"

    conn = get_db()
    # Check if character already exists to avoid duplicates
    existing = query_db("SELECT id FROM characters WHERE name = ? COLLATE NOCASE", (name,), one=True)
    if existing:
        print(f"DB: Character '{name}' already exists. Skipping add.")
        return existing['id']

    cur = conn.execute("""
        INSERT INTO characters 
        (name, description, traits, voice_id, length_scale, noise_scale, noise_w, signature_tic, narrative_role, leitmotif_path) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, description, traits, voice_id, length_scale, noise_scale, noise_w, signature_tic, narrative_role, leitmotif_path))
    conn.commit()
    char_id = cur.lastrowid
    memory_engine.add_character_vector(name, description, traits, char_id)
    return char_id

def update_character_last_seen(char_id, turn_number):
    execute_db("UPDATE characters SET last_seen_turn = ? WHERE id = ?", (turn_number, char_id))

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
    return query_db("SELECT id, description, status FROM plot_threads WHERE status = 'active'")

def update_plot_thread_status(thread_id, status):
    execute_db("UPDATE plot_threads SET status = ? WHERE id = ?", (status, thread_id))

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

def get_recent_sim_events(limit=3):
    return query_db("SELECT * FROM simulation_history ORDER BY id DESC LIMIT ?", (limit,))

def set_story_state(key, value):
    execute_db("INSERT OR REPLACE INTO story_state (key, value) VALUES (?, ?)", (key, value))

def get_story_state(key):
    result = query_db("SELECT value FROM story_state WHERE key = ?", (key,), one=True)
    return result['value'] if result else None

# World Map Functions
def add_location(name, description, x, y, biome_type, elevation=0, climate='Temperate', region_id=None):
    try:
        conn = get_db()
        cur = conn.execute(
            "INSERT INTO locations (name, description, x, y, biome_type, elevation, climate, region_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, description, x, y, biome_type, elevation, climate, region_id)
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None

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
    parent_id = head['id'] if head else None
    turn_number = (head['turn_number'] + 1) if head else 1
    
    conn = get_db()
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
    conn = get_db()
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
    if not quests:
        return []
        
    quest_ids = [q['id'] for q in quests]
    placeholders = ",".join("?" for _ in quest_ids)
    all_objs = query_db(f"SELECT * FROM quest_objectives WHERE quest_id IN ({placeholders}) AND status = 'active'", tuple(quest_ids))
    
    objs_by_quest = {}
    if all_objs:
        for obj in all_objs:
            objs_by_quest.setdefault(obj['quest_id'], []).append(dict(obj))
            
    full_quests = []
    for q in quests:
        q_dict = dict(q)
        q_dict['objectives'] = objs_by_quest.get(q['id'], [])
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

def get_all_relationships():
    return query_db("SELECT * FROM relationships")

def update_relationship(char_a_id, char_b_id, delta_trust, delta_fear, delta_affection, event_desc):
    a, b = min(char_a_id, char_b_id), max(char_a_id, char_b_id)
    
    conn = get_db()
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

# Adventure Arc Functions
def set_active_arc(arc_json):
    set_story_state("active_arc", json.dumps(arc_json))
    set_story_state("current_milestone_index", "0")

def get_active_arc():
    arc_str = get_story_state("active_arc")
    return json.loads(arc_str) if arc_str else None

def get_current_milestone_index():
    idx = get_story_state("current_milestone_index")
    return int(idx) if idx is not None else -1

def set_current_milestone_index(index):
    set_story_state("current_milestone_index", str(index))

# Inventory & Stats Functions
def add_inventory_item(entity_type, entity_id, item_name, description="", quantity=1):
    conn = get_db()
    # Check if item exists
    existing = query_db("SELECT id, quantity FROM inventory WHERE entity_type = ? AND entity_id = ? AND item_name = ?", 
                       (entity_type, entity_id, item_name), one=True)
    if existing:
        conn.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (quantity, existing['id']))
    else:
        conn.execute("INSERT INTO inventory (entity_type, entity_id, item_name, description, quantity) VALUES (?, ?, ?, ?, ?)",
                    (entity_type, entity_id, item_name, description, quantity))
    conn.commit()

def remove_inventory_item(entity_type, entity_id, item_name, quantity=1):
    existing = query_db("SELECT id, quantity FROM inventory WHERE entity_type = ? AND entity_id = ? AND item_name = ?", 
                       (entity_type, entity_id, item_name), one=True)
    if existing:
        if existing['quantity'] <= quantity:
            execute_db("DELETE FROM inventory WHERE id = ?", (existing['id'],))
        else:
            execute_db("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", (quantity, existing['id']))

def get_inventory(entity_type, entity_id):
    return query_db("SELECT * FROM inventory WHERE entity_type = ? AND entity_id = ?", (entity_type, entity_id))

def set_entity_stat(entity_type, entity_id, stat_name, stat_value):
    execute_db("INSERT OR REPLACE INTO entity_stats (entity_type, entity_id, stat_name, stat_value) VALUES (?, ?, ?, ?)",
               (entity_type, entity_id, stat_name, str(stat_value)))

def get_entity_stats(entity_type, entity_id):
    return query_db("SELECT * FROM entity_stats WHERE entity_type = ? AND entity_id = ?", (entity_type, entity_id))

if __name__ == "__main__":
    print("Initializing database...")
    init_db()