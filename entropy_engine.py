import db
import llm
import config
import math
import random
import json

class EntropyEngine:
    def __init__(self):
        self.decay_rate = 0.1 # 10% drift towards 0 per tick
        self.lore_mutation_chance = 0.05 # 5% chance per tick to mutate a minor lore fact
        
    async def run_tick(self, tick_number):
        """
        Advances the entropy logic, causing relationships to decay and minor lore to mutate.
        """
        print(f"EntropyEngine: Running decay for tick {tick_number}...")
        self.decay_relationships()
        await self.mutate_lore()
        
    def decay_relationships(self):
        """
        Moves all relationship scores slightly towards 0.
        """
        relationships = db.get_all_relationships()
        for rel in relationships:
            trust = rel['trust']
            fear = rel['fear']
            affection = rel['affection']
            
            # Decay towards 0
            new_trust = self._decay_value(trust)
            new_fear = self._decay_value(fear)
            new_affection = self._decay_value(affection)
            
            if new_trust != trust or new_fear != fear or new_affection != affection:
                db.execute_db("""
                    UPDATE relationships 
                    SET trust = ?, fear = ?, affection = ?
                    WHERE id = ?
                """, (new_trust, new_fear, new_affection, rel['id']))

    def _decay_value(self, value):
        if value == 0:
            return 0
        
        decay_amount = max(1, int(abs(value) * self.decay_rate))
        
        if value > 0:
            return value - decay_amount
        else:
            return value + decay_amount

    async def mutate_lore(self):
        """
        Randomly mutates a piece of lore to simulate rumors or the passage of time.
        """
        if random.random() > self.lore_mutation_chance:
            return

        all_lore = db.query_db("SELECT * FROM lore")
        if not all_lore:
            return
            
        target = random.choice(all_lore)
        
        prompt = f"""
[SYSTEM: You are the Rumor Mill. Your job is to slightly distort or exaggerate a piece of world lore, as if it has been passed down through generations or spread by gossip.

ORIGINAL LORE:
Topic: {target['topic']}
Description: {target['description']}

Modify the description slightly. Add a rumor, exaggerate a detail, or make it slightly inaccurate. Keep it brief.
REPLY ONLY WITH THE NEW DESCRIPTION.]
"""
        new_desc = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
        
        if new_desc and len(new_desc.strip()) > 10:
            db.execute_db("UPDATE lore SET description = ? WHERE id = ?", (new_desc.strip(), target['id']))
            print(f"Entropy: Lore '{target['topic']}' mutated into rumor.")
