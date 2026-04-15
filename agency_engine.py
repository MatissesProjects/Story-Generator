import db
import llm
import config
import asyncio
import json
import random
import world_engine
import social_engine

class AgencyEngine:
    def __init__(self):
        self.need_decay_rate = 5 # Points per tick
        self.action_recovery = 30 # Points recovered per successful action
        self.world = world_engine.WorldEngine()

    async def run_tick(self, tick_number):
        """
        Advances the agency logic for all NPCs.
        """
        characters = db.get_all_characters()
        actions_taken = []

        for char in characters:
            # 1. Decay Needs
            social = max(0, char['social'] - self.need_decay_rate)
            ambition = max(0, char['ambition'] - self.need_decay_rate)
            safety = max(0, char['safety'] - self.need_decay_rate)
            resources = max(0, char['resources'] - self.need_decay_rate)

            # 2. Decide Action (Utility AI)
            # Check if currently traveling
            pos = db.get_entity_position("character", char['id'])
            if pos and pos['destination_id']:
                priority_action = "Travel"
            else:
                needs = {
                    "Socialize": social,
                    "Work": ambition,
                    "Seek Safety": safety,
                    "Gather Resources": resources
                }
                
                # Find lowest need
                priority_action = min(needs, key=needs.get)
                
                # If the lowest need is still very high, maybe Move or Idle
                if needs[priority_action] > 80:
                    # 30% chance to move if bored, else Idle
                    priority_action = "Move" if random.random() < 0.3 else "Idle"

            # 3. Execute & Narrate
            action_desc, new_needs = await self.process_npc_action(char, priority_action, {
                "social": social, "ambition": ambition, "safety": safety, "resources": resources
            })
            
            # 4. Update DB
            db.update_character_needs(
                char['id'], 
                new_needs['social'], new_needs['ambition'], new_needs['safety'], new_needs['resources'],
                goal=priority_action,
                task=action_desc
            )
            
            actions_taken.append({
                "char_id": char['id'],
                "char_name": char['name'],
                "action": priority_action,
                "description": action_desc
            })

        return actions_taken

    async def process_npc_action(self, char, action, current_needs):
        """
        Determines the outcome and narrative description of an NPC action.
        """
        new_needs = current_needs.copy()
        
        if action == "Idle":
            return f"{char['name']} is going about their daily routine.", new_needs

        if action == "Travel":
            # Advance travel progress
            pos = db.get_entity_position("character", char['id'])
            # Simplified: just arrive for now
            dest = db.get_location(pos['destination_id'])
            db.set_entity_position("character", char['id'], dest['id'])
            # Clear destination
            db.execute_db("UPDATE entity_positions SET destination_id = NULL WHERE entity_type = 'character' AND entity_id = ?", (char['id'],))
            return f"{char['name']} arrived at {dest['name']}.", new_needs

        if action == "Move":
            # Pick a random connected location or just a random one for now
            all_locs = db.get_all_locations()
            if len(all_locs) > 1:
                target = random.choice([l for l in all_locs if l['name'] != char.get('current_location')])
                db.execute_db("UPDATE entity_positions SET destination_id = ? WHERE entity_type = 'character' AND entity_id = ?", (target['id'], char['id']))
                return f"{char['name']} set off for {target['name']}.", new_needs
            return f"{char['name']} considered traveling, but stayed put.", new_needs

        if action == "Socialize":
            # Find someone else at the same location
            my_pos = db.get_entity_position("character", char['id'])
            if my_pos:
                others = db.query_db("SELECT * FROM entity_positions WHERE current_location_id = ? AND (entity_type != 'character' OR entity_id != ?)", 
                                    (my_pos['current_location_id'], char['id']))
                if others:
                    target = random.choice(others)
                    target_name = "the player" if target['entity_type'] == 'player' else f"another character"
                    # Log social recovery
                    new_needs['social'] += self.action_recovery
                    return f"{char['name']} spent time talking with {target_name}.", new_needs

        # Default: Use LLM for narration of generic needs
        prompt = f"""
[SYSTEM: You are the NPC Agency Narrator. A character is acting on their own will.
CHARACTER: {char['name']}
TRAITS: {char['traits']}
CHOSEN ACTION: {action}

Write a single, concise sentence describing what this character did. 
Be specific to their traits. Do not mention "meters" or "stats".
REPLY ONLY WITH THE DESCRIPTION.]
"""
        description = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
        
        # Recover the need
        if action == "Socialize": new_needs['social'] += self.action_recovery
        elif action == "Work": new_needs['ambition'] += self.action_recovery
        elif action == "Seek Safety": new_needs['safety'] += self.action_recovery
        elif action == "Gather Resources": new_needs['resources'] += self.action_recovery
        
        # Clamp to 100
        for k in new_needs:
            new_needs[k] = min(100, new_needs[k])
            
        return description.strip(), new_needs
