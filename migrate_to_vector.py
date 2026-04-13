import db
import memory_engine
import os

def migrate():
    print("Starting migration from SQLite to Vector DB...")
    
    # Migrate Lore
    lore_entries = db.query_db("SELECT * FROM lore")
    for lore in lore_entries:
        print(f"Indexing Lore: {lore['topic']}")
        memory_engine.add_lore_vector(lore['topic'], lore['description'], lore['id'])
        
    # Migrate Characters
    char_entries = db.query_db("SELECT * FROM characters")
    for char in char_entries:
        print(f"Indexing Character: {char['name']}")
        memory_engine.add_character_vector(char['name'], char['description'], char['traits'], char['id'])
        
    print("Migration complete!")

if __name__ == "__main__":
    if os.path.exists(db.DB_PATH):
        migrate()
    else:
        print("No SQLite DB found to migrate.")
