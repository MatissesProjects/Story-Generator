CREATE TABLE IF NOT EXISTS characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    traits TEXT,
    voice_id TEXT
);

CREATE TABLE IF NOT EXISTS lore (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS plot_threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS timeline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_description TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS meta_lore (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    description TEXT NOT NULL,
    keywords TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_input TEXT,
    assistant_response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS story_state (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS regions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    theme TEXT,
    security_level INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    biome_type TEXT,
    elevation INTEGER DEFAULT 0,
    climate TEXT DEFAULT 'Temperate',
    region_id INTEGER,
    FOREIGN KEY (region_id) REFERENCES regions(id)
);

CREATE TABLE IF NOT EXISTS paths (
    from_id INTEGER,
    to_id INTEGER,
    distance REAL,
    path_type TEXT,
    PRIMARY KEY (from_id, to_id),
    FOREIGN KEY (from_id) REFERENCES locations(id),
    FOREIGN KEY (to_id) REFERENCES locations(id)
);

CREATE TABLE IF NOT EXISTS entity_positions (
    entity_type TEXT, -- 'player' or 'character'
    entity_id INTEGER,
    current_location_id INTEGER,
    destination_id INTEGER,
    travel_progress REAL DEFAULT 0.0,
    PRIMARY KEY (entity_type, entity_id),
    FOREIGN KEY (current_location_id) REFERENCES locations(id),
    FOREIGN KEY (destination_id) REFERENCES locations(id)
);

CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER,
    session_id TEXT NOT NULL,
    turn_number INTEGER NOT NULL,
    branch_name TEXT DEFAULT 'main',
    narrative_seed TEXT, -- The Story So Far at this point
    user_input TEXT,
    assistant_response TEXT,
    location_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES snapshots(id),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);

CREATE TABLE IF NOT EXISTS story_heads (
    session_id TEXT PRIMARY KEY,
    current_snapshot_id INTEGER,
    active_branch TEXT DEFAULT 'main',
    FOREIGN KEY (current_snapshot_id) REFERENCES snapshots(id)
);

CREATE TABLE IF NOT EXISTS quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 1, -- 1: Low, 5: Critical
    status TEXT DEFAULT 'active' -- active, completed, failed, abandoned
);

CREATE TABLE IF NOT EXISTS quest_objectives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quest_id INTEGER,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    FOREIGN KEY (quest_id) REFERENCES quests(id)
);

CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    char_a_id INTEGER, -- 0 for Player
    char_b_id INTEGER,
    trust INTEGER DEFAULT 0,
    fear INTEGER DEFAULT 0,
    affection INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(char_a_id, char_b_id)
);

CREATE TABLE IF NOT EXISTS interaction_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    char_a_id INTEGER,
    char_b_id INTEGER,
    event_description TEXT NOT NULL,
    delta_trust INTEGER DEFAULT 0,
    delta_fear INTEGER DEFAULT 0,
    delta_affection INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS foreshadowed_elements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        element_name TEXT NOT NULL,
        discovery_location TEXT,
        potential_impact TEXT,
        payoff_status TEXT DEFAULT 'pending' -- pending, resolved
    );

    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_type TEXT NOT NULL, -- 'player' or 'character'
        entity_id INTEGER NOT NULL,
        item_name TEXT NOT NULL,
        description TEXT,
        quantity INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS entity_stats (
        entity_type TEXT NOT NULL, -- 'player' or 'character'
        entity_id INTEGER NOT NULL,
        stat_name TEXT NOT NULL,
        stat_value TEXT NOT NULL,
        PRIMARY KEY (entity_type, entity_id, stat_name)
    );