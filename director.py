import db
import llm
import researcher
import world_engine
import config
import random
import json

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

def check_narrative_gaps(recent_history, active_threads):
    """
    Uses the LLM to analyze if the story has stalled or become repetitive.
    Returns (needs_research, suggested_theme)
    """
    history_text = "\n".join([f"P: {h['user_input']}\nS: {h['assistant_response']}" for h in recent_history])
    threads_text = "\n".join([f"- {t['description']}" for t in active_threads])
    
    prompt = f"""
[SYSTEM: You are the Narrative Architect. Analyze the recent story history and active plot threads. 
Your goal is to decide if the story is becoming "stale," "repetitive," or "predictable." 

STORY HISTORY:
{history_text}

ACTIVE PLOT THREADS:
{threads_text}

If the story is moving well, reply with: {{"needs_research": false, "suggested_theme": ""}}
If the story needs a "crazy new idea" or fresh lore to stay interesting, reply with: {{"needs_research": true, "suggested_theme": "A broad theme for research, e.g., 'underground ecosystems', 'forgotten alchemy', 'weird parasites'"}}

REPLY ONLY IN JSON.]
"""
    response = ""
    for chunk in llm.generate_story_segment(prompt):
        response += chunk
        
    try:
        # Basic JSON extraction
        clean_json = response.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        result = json.loads(clean_json)
        return result.get("needs_research", False), result.get("suggested_theme", "")
    except Exception as e:
        print(f"Director Error (parsing JSON): {e}. Raw: {response}")
        return False, ""

def identify_location(user_input, recent_history):
    """
    Uses the LLM to identify if the story has moved to a new location.
    Returns (location_name, description) or (None, None).
    """
    history_text = "\n".join([f"P: {h['user_input']}\nS: {h['assistant_response']}" for h in recent_history[-3:]])
    
    prompt = f"""
[SYSTEM: You are the Scene Parser. Analyze the recent story history and determine the current physical location of the player.

RECENT HISTORY:
{history_text}

NEW INPUT:
"{user_input}"

If the location has changed or is explicitly named for the first time, reply with JSON: {
    "location": "Name of Location", 
    "description": "Brief atmospheric description",
    "relative_to": "Name of a previous location if known, else null",
    "direction": "north/south/east/west/etc if implied, else null"
}
If the location is the same as before or unclear, reply with JSON: {"location": null, "description": null, "relative_to": null, "direction": null}

REPLY ONLY IN JSON.]
"""
    response = ""
    for chunk in llm.generate_story_segment(prompt):
        response += chunk
        
    try:
        clean_json = response.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        result = json.loads(clean_json)
        return result.get("location"), result.get("description"), result.get("relative_to"), result.get("direction")
    except Exception as e:
        print(f"Director Error (identify_location): {e}. Raw: {response}")
        return None, None, None, None

if __name__ == "__main__":
    # Test
    print("Testing Director Agent...")
    db.init_db()
    db.add_plot_thread("The silver locket was stolen by a goblin.")
    print(evaluate_state("I walk into the cave."))