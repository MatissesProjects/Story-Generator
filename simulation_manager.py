import db
import llm
import config
import asyncio
import json

async def trigger_tick():
    """
    Advances the global simulation by one tick.
    Coordinates updates across all world systems.
    """
    # 1. Advance Time
    current_time = int(db.get_story_state("world_time") or 0)
    new_time = current_time + 1
    db.set_story_state("world_time", str(new_time))
    
    print(f"Simulation: Tick {new_time} triggered.")
    
    # 2. Run Scheduled Updates (Basic for now)
    events = []
    
    # Every tick, there's a chance of a minor world event
    if new_time % 1 == 0:
        event = await generate_background_event(new_time)
        if event:
            events.append(event)

    # 3. Log Events
    for e in events:
        db.execute_db(
            "INSERT INTO simulation_history (tick_number, event_type, description, location_id) VALUES (?, ?, ?, ?)",
            (new_time, e.get('type', 'General'), e.get('description', ''), e.get('location_id'))
        )
        print(f"Simulation Event: {e.get('description')}")

    return events

async def generate_background_event(tick_number):
    """
    Uses the LLM to generate a "hidden" event that happens somewhere in the world.
    """
    # Get some context to make it relevant
    locations = db.get_all_locations()
    loc_context = ""
    if locations:
        # Pick 3 random locations for variety
        import random
        sampled = random.sample(locations, min(len(locations), 3))
        loc_context = "LOCATIONS:\n" + "\n".join([f"- {l['name']}: {l['description']}" for l in sampled])

    prompt = f"""
[SYSTEM: You are the World Orchestrator. A unit of time (Tick {tick_number}) has passed.
Your goal is to generate a single "Background Event" that happened somewhere in the world.
This event should be interesting, narrative-driven, and potentially affect future player interactions.

{loc_context}

EXAMPLES:
- "A heavy storm has washed out the bridge near The Dusty Tavern."
- "Rumors of a gold strike are drawing prospectors to the Peak of Doom."
- "The local magistrate in the Silver City has passed a new tax on magic."

Reply ONLY with a JSON object:
{{
    "type": "Environmental/Political/Social/Economic",
    "description": "Short description of the event",
    "location_name": "Name of location if applicable, else null",
    "impact_level": 1 to 5
}}
]
"""
    response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
    try:
        clean_json = response.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        data = json.loads(clean_json)
        
        # Resolve location name to ID if provided
        if data.get('location_name'):
            loc = db.get_location_by_name(data['location_name'])
            if loc:
                data['location_id'] = loc['id']
                
        return data
    except Exception as e:
        print(f"Simulation Error (generate_background_event): {e}")
        return None

if __name__ == "__main__":
    # Test tick
    async def test():
        await trigger_tick()
    asyncio.run(test())
