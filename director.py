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
        return None
        
    notes_str = "\n".join(context_notes)
    instruction = f"DIRECTOR'S NOTE: Keep the following narrative goals in mind as 'gentle suggestions'. Do not force them if the story naturally wanders, but look for subtle ways to integrate them: \n{notes_str}"
    
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

If an objective is completed, reply with JSON: {{"updates": [{{"objective_id": 123, "status": "completed"}}]}}
If no progress was made, reply with JSON: {{"updates": []}}

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

If the criteria have been met, reply with JSON: {{"completed": true}}
Else, reply with JSON: {{"completed": false}}

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

If the story is moving well, reply with: {{"needs_research": false, "suggested_theme": ""}}
If the story needs a "crazy new idea" or fresh lore to stay interesting, reply with: {{"needs_research": true, "suggested_theme": "A broad theme for research, e.g., 'underground ecosystems', 'forgotten alchemy', 'weird parasites'"}}

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

async def identify_location(user_input, recent_history):
    """
    Uses the LLM to identify if the story has moved to a new location.
    Returns (location_name, description, relative_to, direction) or (None, None, None, None).
    """
    history_text = "\n".join([f"P: {h['user_input']}\nS: {h['assistant_response']}" for h in recent_history[-3:]])
    
    prompt = f"""
[SYSTEM: You are the Scene Parser. Analyze the recent story history and determine the current physical location of the player.

RECENT HISTORY:
{history_text}

NEW INPUT:
"{user_input}"

If the location has changed or is explicitly named for the first time, reply with JSON: {{
    "location": "Name of Location", 
    "description": "Brief atmospheric description",
    "relative_to": "Name of a previous location if known, else null",
    "direction": "north/south/east/west/etc if implied, else null"
}}
If the location is the same as before or unclear, reply with JSON: {{"location": null, "description": null, "relative_to": null, "direction": null}}

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

async def generate_action_plan(user_input, recent_history, active_threads, active_quests):
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
        identify_location(user_input, recent_history)
    )
    
    plan["needs_research"], plan["research_theme"] = results[0]
    plan["quest_updates"] = results[1]
    plan["milestone_completed"] = results[2]
    loc_name, loc_desc, rel_to, direction = results[3]
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
- "Constantly polishes a small silver coin between her knuckles."
- "Never looks people in the eye, instead staring at their throat."
- "Taps a rhythmic code on any wooden surface nearby."

REPLY ONLY WITH THE TIC DESCRIPTION (one sentence).]
"""
    return await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)

if __name__ == "__main__":
    # Test
    print("Testing Director Agent...")
    db.init_db()
    db.add_plot_thread("The silver locket was stolen by a goblin.")
    print(evaluate_state("I walk into the cave."))
