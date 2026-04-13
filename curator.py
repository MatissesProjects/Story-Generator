import db

def get_relevant_context(user_input):
    """
    Scans the user input for character names or lore topics 
    and returns a list of matching details.
    """
    entities = db.get_all_entities()
    matches = []
    
    # Simple keyword matching for now
    for entity in entities:
        if entity.lower() in user_input.lower():
            # Check characters
            char_results = db.search_characters(entity)
            for char in char_results:
                matches.append(f"CHARACTER: {char['name']} - {char['description']} (Traits: {char['traits']})")
            
            # Check lore
            lore_results = db.search_lore(entity)
            for lore in lore_results:
                matches.append(f"LORE: {lore['topic']} - {lore['description']}")
                
    # Also include active plot threads
    active_plots = db.query_db("SELECT * FROM plot_threads WHERE status = 'active'")
    for plot in active_plots:
        matches.append(f"ACTIVE PLOT: {plot['description']}")
        
    return list(set(matches)) # De-duplicate

if __name__ == "__main__":
    # Test curator
    print("Testing Context Curator...")
    # Add a dummy character and lore point
    db.execute_db("INSERT INTO characters (name, description, traits) VALUES (?, ?, ?)", 
                   ("Malakar", "A shadowy assassin", "Swift, Ruthless"))
    db.execute_db("INSERT INTO lore (topic, description) VALUES (?, ?)", 
                   ("The Void", "A realm of darkness between stars"))
    
    print(f"Context for 'Malakar entered the Void':")
    for fact in get_relevant_context("Malakar entered the Void"):
        print(f"- {fact}")
    
    # Clean up
    db.execute_db("DELETE FROM characters WHERE name = 'Malakar'")
    db.execute_db("DELETE FROM lore WHERE topic = 'The Void'")
    print("Test complete.")