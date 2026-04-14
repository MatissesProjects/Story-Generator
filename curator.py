import db
import memory_engine

def get_relevant_context(user_input):
    """
    Scans the user input for character names or lore topics (Keyword)
    AND performs a semantic search for related themes/facts.
    """
    entities = db.get_all_entities()
    matches = []
    
    # 1. Keyword Matching (Exact/Partial)
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
                
    # 2. Semantic Search (Thematic/Conceptual)
    semantic_facts = memory_engine.search_semantic(user_input, n_results=3, threshold=0.4)
    matches.extend(semantic_facts)

    # 3. Active Plot Threads
    active_plots = db.query_db("SELECT * FROM plot_threads WHERE status = 'active'")
    for plot in active_plots:
        matches.append(f"ACTIVE PLOT: {plot['description']}")

    # 4. Active Leads (Quests)
    quests = db.get_active_quests()
    for q in quests:
        obj_text = ", ".join([obj['description'] for obj in q['objectives']])
        matches.append(f"ACTIVE LEAD: {q['title']} - {q['description']} (Objectives: {obj_text})")
        
    # --- Meta-Narrative Thematic Resonance (Track 6) ---
    meta_lore = db.get_all_meta_lore()
    for meta in meta_lore:
        keywords = [k.strip().lower() for k in meta['keywords'].split(",")]
        for kw in keywords:
            if kw in user_input.lower():
                matches.append(f"[META-NARRATIVE BLEED: The concept of '{meta['topic']}' is subtly affecting this world: {meta['description']}. Hint at this atmosphere or theme briefly, but do not make it the main focus of the scene.]")
                break # Only add once per meta-lore topic
    
    return list(set(matches)) # De-duplicate

if __name__ == "__main__":
    # Test curator
    print("Testing Context Curator...")
    # Add a dummy character, lore point, and meta-lore
    db.add_character("Malakar", "A shadowy assassin", "Swift, Ruthless")
    db.add_lore("The Void", "A realm of darkness between stars")
    db.add_meta_lore("The Chroma Drain", "Shadows are slowly disappearing from the multiverse", "shadow, dark, void")

    print(f"Context for 'Malakar entered the Void':")
    for fact in get_relevant_context("Malakar entered the Void"):
        print(f"- {fact}")

    # Clean up
    db.execute_db("DELETE FROM characters WHERE name = 'Malakar'")
    db.execute_db("DELETE FROM lore WHERE topic = 'The Void'")
    db.execute_db("DELETE FROM meta_lore WHERE topic = 'The Chroma Drain'")
    print("Test complete.")