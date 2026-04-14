import db
import llm
import researcher
import config
import random

def evaluate_state(user_input, recent_history=None):
    """
    Analyzes the current story state and plot threads.
    Generates hidden 'Director Instructions' to nudge the story.
    """
    plot_threads = db.get_active_plot_threads()
    if not plot_threads:
        return None
        
    threads_text = "\n".join([f"- {t['description']}" for t in plot_threads])
    
    # Simple logic: If we have active threads, remind the LLM of one or two
    # In a more advanced version, we could use an LLM call here to decide *which* one to nudge
    
    # For now, let's just provide the active threads as context for the 'Director'
    instruction = f"DIRECTOR'S NOTE: Keep the following unresolved plot points in mind and look for opportunities to develop them: {threads_text}"
    
    return instruction

def get_persona_blocks(user_input):
    """
    Identifies characters mentioned in the input and retrieves their persona constraints.
    """
    entities = db.get_all_entities()
    persona_blocks = []
    
    for entity in entities:
        if entity.lower() in user_input.lower():
            char_results = db.search_characters(entity)
            for char in char_results:
                # Format: [SPEAKER: {Name}; TRAITS: {Traits}; CURRENT_MOOD: {Mood}; HIDDEN_GOAL: {Goal}]
                # Note: Mood and Hidden Goal could be dynamic in future iterations
                block = f"[SPEAKER: {char['name']}; TRAITS: {char['traits']}; DESCRIPTION: {char['description']}]"
                persona_blocks.append(block)
                
    return persona_blocks

if __name__ == "__main__":
    # Test
    print("Testing Director Agent...")
    db.init_db()
    db.add_plot_thread("The silver locket was stolen by a goblin.")
    print(evaluate_state("I walk into the cave."))