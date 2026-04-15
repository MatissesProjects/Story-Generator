import db
import memory_engine

def get_relevant_context(user_input, top_n=5):
    """
    Scans the user input for character names or lore topics (Keyword)
    AND performs a semantic search for related themes/facts.
    Returns a ranked list of context strings.
    """
    entities = db.get_all_entities()
    matches = [] # List of (score, fact_string)
    
    user_input_lower = user_input.lower()

    # 1. Keyword Matching (Exact/Partial) - High Score (1.0)
    for entity in entities:
        if entity.lower() in user_input_lower:
            # Check characters
            char_results = db.search_characters(entity)
            for char in char_results:
                matches.append((1.0, f"CHARACTER: {char['name']} - {char['description']} (Traits: {char['traits']})"))
            
            # Check lore
            lore_results = db.search_lore(entity)
            for lore in lore_results:
                matches.append((1.0, f"LORE: {lore['topic']} - {lore['description']}"))
                
    # 2. Semantic Search (Thematic/Conceptual) - Medium Score (0.5 to 0.8)
    semantic_results = memory_engine.search_semantic_with_scores(user_input, n_results=5, threshold=0.4)
    for fact, score in semantic_results:
        # Normalize score (chroma distance -> 0 to 1, where lower is better usually)
        # Assuming score here is similarity where higher is better or distance where lower is better.
        # Let's just use it as is for now or flip if it's distance.
        matches.append((0.7, fact))

    # 3. Active Plot Threads - Medium Score (0.6)
    active_plots = db.query_db("SELECT * FROM plot_threads WHERE status = 'active'")
    for plot in active_plots:
        matches.append((0.6, f"ACTIVE PLOT: {plot['description']}"))

    # 4. Active Leads (Quests) - Medium Score (0.6)
    quests = db.get_active_quests()
    for q in quests:
        obj_text = ", ".join([obj['description'] for obj in q['objectives']])
        matches.append((0.6, f"ACTIVE LEAD: {q['title']} - {q['description']} (Objectives: {obj_text})"))
        
    # 5. Meta-Narrative Thematic Resonance - Contextual Score (0.5)
    meta_lore = db.get_all_meta_lore()
    for meta in meta_lore:
        keywords = [k.strip().lower() for k in meta['keywords'].split(",")]
        for kw in keywords:
            if kw in user_input_lower:
                matches.append((0.5, f"[META-NARRATIVE BLEED: The concept of '{meta['topic']}' is subtly affecting this world: {meta['description']}. Hint at this atmosphere or theme briefly, but do not make it the main focus of the scene.]"))
                break 

    # Sort by score descending and take top N
    matches.sort(key=lambda x: x[0], reverse=True)
    
    # De-duplicate by fact string
    seen = set()
    final_matches = []
    for score, fact in matches:
        if fact not in seen:
            final_matches.append(fact)
            seen.add(fact)
            if len(final_matches) >= top_n:
                break
                
    return final_matches

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