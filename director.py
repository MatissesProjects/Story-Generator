import db
import llm
import researcher
import world_engine
import config
import random
import json
import asyncio

def evaluate_state(user_input, recent_history=None):
    """
    Analyzes the current story state and plot threads.
    Generates hidden 'Director Instructions' to nudge the story.
    """
    plot_threads = db.get_active_plot_threads()
    active_quests = db.get_active_quests()
    
    context_notes = []
    
    if plot_threads:
        threads_text = "\n".join([f"- {t['description']}" for t in plot_threads])
        context_notes.append(f"PLOT POINTS: {threads_text}")
        
    if active_quests:
        quests_text = "\n".join([f"- {q['title']}: {q['description']}" for q in active_quests])
        context_notes.append(f"ACTIVE LEADS: {quests_text}")

    if not context_notes:
        notes_str = "No specific plot threads active."
    else:
        notes_str = "\n".join(context_notes)
        
    instruction = f"""
DIRECTOR'S NOTE: Keep the following narrative goals in mind as 'gentle suggestions'. Do not force them if the story naturally wanders, but look for subtle ways to integrate them: 
{notes_str}

CORE NARRATIVE DIRECTIVE: Do NOT provide numbered lists of options. Instead, be PROACTIVE. 
Describe environmental shifts, sudden character actions, or mysterious discoveries that force the player to react to the world's changing state.
"""
    
    return instruction

async def evaluate_quest_progress(history_text):
    """
    Uses the LLM to check if any quest objectives were met in the recent history.
    Returns a list of (quest_id, objective_id, status) updates.
    """
    active_quests = db.get_active_quests()
    if not active_quests:
        return []
        
    quests_json = json.dumps([{
        "id": q['id'], 
        "title": q['title'], 
        "objectives": [{"id": o['id'], "desc": o['description']} for o in q['objectives']]
    } for q in active_quests])
    
    prompt = f"""
    [SYSTEM: You are the Quest Arbiter. Analyze the following story segment and decide if any active quest objectives have been COMPLETED or FAILED.

    STORY SEGMENT:
    "{history_text}"

    ACTIVE QUESTS:
    {quests_json}

    If an objective is completed, reply with JSON: 
    EXAMPLE STRUCTURE (Do not use these specific values):
    {{ "updates": [{{ "objective_id": 123, "status": "completed" }}] }}
    
    If no progress was made, reply with JSON: {{ "updates": [] }}

    BE CONSERVATIVE. Only mark as completed if it clearly happened in the text.
    REPLY ONLY IN JSON.]
    """
    response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
        
    try:
        clean_json = response.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        result = json.loads(clean_json)
        return result.get("updates", [])
    except Exception as e:
        print(f"Director Error (evaluate_quest_progress): {e}. Raw: {response}")
        return []

async def evaluate_milestone_progress(history_text):
    """
    Checks if the current active arc milestone has been completed.
    """
    arc = db.get_active_arc()
    if not arc:
        return False
        
    idx = db.get_current_milestone_index()
    if idx < 0 or idx >= len(arc['milestones']):
        return False
        
    milestone = arc['milestones'][idx]
    
    prompt = f"""
[SYSTEM: You are the Narrative Milestone Arbiter. Analyze the recent story history and determine if the current milestone has been achieved.

MILESTONE: {milestone['name']}
DESCRIPTION: {milestone['description']}
COMPLETION CRITERIA: {milestone['completion_criteria']}

RECENT HISTORY:
"{history_text}"

Reply ONLY with a JSON object.
EXAMPLE STRUCTURE (Do not use these specific values):
{{
    "completed": true
}}

REPLY ONLY IN JSON.]
"""
    response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
        
    try:
        clean_json = response.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        result = json.loads(clean_json)
        return result.get("completed", False)
    except Exception as e:
        print(f"Director Error (evaluate_milestone_progress): {e}. Raw: {response}")
        return False

def get_persona_blocks(user_input, current_turn=0):
    """
    Identifies characters mentioned in the input and retrieves their persona constraints,
    relationships, roles, and signature tics.
    """
    entities = db.get_all_entities()
    persona_blocks = []

    for entity in entities:
        if entity.lower() in user_input.lower():
            char_results = db.search_characters(entity)
            for char in char_results:
                # Update last seen turn
                db.update_character_last_seen(char['id'], current_turn)

                # Get relationship with player (id 0)
                rel = db.get_relationship(0, char['id'])
                rel_str = f"RELATIONSHIP WITH PLAYER: Trust {rel['trust']}, Fear {rel['fear']}, Affection {rel['affection']}"

                # Role and Tic
                role_str = f"NARRATIVE ROLE: {char['narrative_role']}"
                tic_str = f"SIGNATURE TIC (Anchor): {char['signature_tic'] or 'None'}"

                # Check for "Reunion" (long absence)
                reunion_note = ""
                if current_turn - char['last_seen_turn'] > 15:
                    reunion_note = f"\nREUNION EVENT: {char['name']} hasn't been seen for a long time. RE-INTRODUCE THEM using their SIGNATURE TIC prominently."

                # Format: [SPEAKER: {Name}; ROLE: {Role}; TRAITS: {Traits}; DESCRIPTION: {Description}; TIC: {Tic}; {RelStr}]
                block = f"[SPEAKER: {char['name']}; {role_str}; TRAITS: {char['traits']}; DESCRIPTION: {char['description']}; {tic_str}; {rel_str}]{reunion_note}"
                persona_blocks.append(block)

    return persona_blocks


async def check_narrative_gaps(recent_history, active_threads):
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

Reply ONLY with a JSON object.
EXAMPLE STRUCTURE (Do not use these specific values):
{{
    "needs_research": true, 
    "suggested_theme": "underground ecosystems"
}}

REPLY ONLY IN JSON.]
"""
    response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
        
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

async def identify_location(user_input, recent_history, current_location=None):
    """
    Uses the LLM to identify if the story has moved to a new location.
    Returns (location_name, description, relative_to, direction) or (None, None, None, None).
    """
    history_text = "\n".join([f"P: {h['user_input']}\nS: {h['assistant_response']}" for h in recent_history[-3:]])
    
    prompt = f"""
[SYSTEM: You are the Scene Parser. Analyze the recent story history and determine if the physical location of the player has CHANGED.
CURRENT LOCATION: {current_location or 'Unknown'}

RECENT HISTORY:
{history_text}

NEW INPUT:
"{user_input}"

Reply ONLY with a JSON object.
If the player has moved to a definitively NEW and distinct location (not just moving within the same general area), provide the details:
{{
    "location": "Name of New Location", 
    "description": "Brief atmospheric description",
    "relative_to": "Previous location",
    "direction": "north"
}}
If the location is the SAME as the CURRENT LOCATION or if the movement is just within the same general area, return null values.

REPLY ONLY IN JSON.]
"""
    response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
        
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

async def generate_creative_name(category, context, theme=None):
    """
    Generates a highly creative name for a character, location, or artifact.
    category: 'character', 'location', 'artifact', 'organization', 'spell'
    """
    theme_str = f"THEME: {theme}" if theme else ""
    prompt = f"""
[SYSTEM: You are the Creative Namer. Your goal is to generate a UNIQUE, EVOCATIVE, and LINGUISTICALLY DIVERSE name for a {category}.

RULES:
1. ABSOLUTELY DO NOT use common fantasy tropes or overused names like 'Kaelen', 'Kael', 'Elias', or 'Aria'.
2. Use diverse naming conventions inspired by real-world linguistics or unique constructed phonetic structures.
3. The name should feel like it belongs in a deep, rich, and mysterious world.
4. Avoid generic, single-syllable, or lazy names.

CONTEXT:
{context}

{theme_str}

Reply ONLY with the name (1-3 words).]
"""
    name = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
    return name.strip().strip('"').strip("'")

async def generate_action_plan(user_input, recent_history, active_threads, active_quests, current_location=None):
    """
    Analyzes the state and generates a structured list of required module actions.
    This coordinates parallel modules.
    """
    plan = {
        "needs_research": False,
        "research_theme": "",
        "quest_updates": [],
        "milestone_completed": False,
        "new_location": None
    }
    
    # Run evaluations in parallel
    results = await asyncio.gather(
        check_narrative_gaps(recent_history, active_threads),
        evaluate_quest_progress(user_input), 
        evaluate_milestone_progress(user_input),
        identify_location(user_input, recent_history, current_location=current_location),
        return_exceptions=True
    )
    
    # Process results with fallbacks for exceptions
    gaps_result = results[0] if not isinstance(results[0], Exception) else (False, "")
    quests_result = results[1] if not isinstance(results[1], Exception) else []
    milestone_result = results[2] if not isinstance(results[2], Exception) else False
    location_result = results[3] if not isinstance(results[3], Exception) else (None, None, None, None)

    plan["needs_research"], plan["research_theme"] = gaps_result
    plan["quest_updates"] = quests_result
    plan["milestone_completed"] = milestone_result
    loc_name, loc_desc, rel_to, direction = location_result
    if loc_name:
        plan["new_location"] = {"name": loc_name, "desc": loc_desc, "rel_to": rel_to, "direction": direction}
        
    return plan

async def generate_initiative(recent_history, active_threads):
    """
    Generates a proactive story event to move the plot forward when it stalls.
    """
    history_text = "\n".join([f"P: {h['user_input']}\nS: {h['assistant_response']}" for h in recent_history[-5:]])
    threads_text = "\n".join([f"- {t['description']}" for t in active_threads])
    
    prompt = f"""
[SYSTEM: You are the Proactive DM. The story has reached a lull. Your goal is to generate a SUDDEN, INTERESTING EVENT that forces the player to react.

STORY HISTORY:
{history_text}

ACTIVE PLOT THREADS:
{threads_text}

Instructions:
1. Pick one of the active plot threads or a character relationship.
2. Create a sudden interruption, a new discovery, or a direct confrontation.
3. Be dramatic and high-stakes.

REPLY ONLY WITH THE EVENT DESCRIPTION.]
"""
    return await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)

async def generate_character_tic(name, description, traits):
    """
    Uses the LLM to generate a memorable physical or behavioral 'anchor' tic for a character.
    """
    prompt = f"""
[SYSTEM: You are the Character Architect. Your goal is to create a single, memorable 'signature tic' or 'anchor' for a character.
This should be a brief physical action, a specific scent, or a recurring behavioral quirk that makes them instantly recognizable.

CHARACTER: {name}
DESCRIPTION: {description}
TRAITS: {traits}

EXAMPLES:
- "Always tugs at his left earlobe when lying."
- "Smells faintly of scorched cinnamon and old parchment."
- "Constantly polishes a small bronze coin between her knuckles."
- "Never looks people in the eye, instead staring at their throat."
- "Taps a rhythmic code on any wooden surface nearby."

REPLY ONLY WITH THE TIC DESCRIPTION (one sentence).]
"""
    return await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)

async def analyze_plot_threads(recent_history, active_threads):
    """
    Analyzes the story history and active threads to identify new threads or resolutions.
    """
    history_text = "\n".join([f"P: {h['user_input']}\nS: {h['assistant_response']}" for h in recent_history])
    threads_json = json.dumps([{"id": t['id'], "description": t['description']} for t in active_threads])
    
    prompt = f"""
[SYSTEM: You are the Plot Thread Analyzer. Your goal is to keep the story's active objectives up to date.
Analyze the recent story history and the list of currently active plot threads.

STORY HISTORY:
{history_text}

ACTIVE PLOT THREADS:
{threads_json}

Your task:
1. Identify if any active plot threads have been RESOLVED or are no longer relevant.
2. Identify if any NEW major plot threads or mysteries have emerged in the recent history.

Reply ONLY with a JSON object.
EXAMPLE STRUCTURE (Do not use these specific values):
{{
    "resolved_ids": [1, 2],
    "new_threads": ["Find the lost city"]
}}

BE CONSERVATIVE. Only add a new thread if it represents a significant goal or mystery.
Only resolve a thread if it has reached a clear conclusion.

REPLY ONLY IN JSON.]
"""
    response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
    
    try:
        clean_json = response.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        return json.loads(clean_json)
    except Exception as e:
        print(f"Director Error (analyze_plot_threads): {e}. Raw: {response}")
        return {"resolved_ids": [], "new_threads": []}

if __name__ == "__main__":
    # Test
    print("Testing Director Agent...")
    db.init_db()
    print(evaluate_state("I walk into the cave."))
