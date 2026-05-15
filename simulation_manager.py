import db
import llm
import config
import asyncio
import json
import agency_engine
import entropy_engine
import utils

agency = agency_engine.AgencyEngine()
entropy = entropy_engine.EntropyEngine()

async def trigger_tick():
    """
    Advances the global simulation by one tick.
    Coordinates updates across all world systems.
    """
    try:
        # 1. Advance Time
        current_time = int(db.get_story_state("world_time") or 0)
        new_time = current_time + 1
        db.set_story_state("world_time", str(new_time))
        
        print(f"Simulation: Tick {new_time} triggered.")
        
        # 2. Run Scheduled Updates
        events = []
        
        # Entropy Logic (Memory Decay & Lore Mutation)
        await entropy.run_tick(new_time)
        
        # NPC Agency Logic
        npc_actions = await agency.run_tick(new_time)
        for action in npc_actions:
            events.append({
                "type": "NPC_Action",
                "description": f"{action['char_name']}: {action['description']}",
                "location_id": action.get('location_id')
            })

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
    except Exception as e:
        print(f"Simulation Manager Critical Error (trigger_tick): {e}")
        return []

async def generate_background_event(tick_number):
    """
    Uses the LLM to generate a "hidden" event that happens somewhere in the world.
    """
    # Get some context to make it relevant
    try:
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

EXAMPLES (Do not use these specific values):
- "A heavy storm has washed out the bridge near The Dusty Tavern."
- "Rumors of a gold strike are drawing prospectors to the Peak of Doom."
- "The local magistrate in the Silver City has passed a new tax on magic."

Reply ONLY with a JSON object.
EXAMPLE STRUCTURE (Do not use these specific values):
{{
    "type": "Environmental",
    "description": "Short description of the event",
    "location_name": "Name of location",
    "impact_level": 1
}}
]
"""
        response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
        data = utils.safe_parse_json(response, default={})
        if not data:
            return None
        
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
