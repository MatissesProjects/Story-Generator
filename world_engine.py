import db
import llm
import json
import random

class WorldEngine:
    def __init__(self):
        self.grid_size = 100 # Arbitrary unit

    def resolve_new_location(self, name, description, relative_to_name=None, direction=None):
        """
        Determines where a new location should be placed on the 2D map.
        If relative_to_name is provided, it tries to place it in the specified direction.
        Otherwise, it places it at (0,0) or a random nearby spot.
        """
        existing = db.get_location_by_name(name)
        if existing:
            return existing['id']

        x, y = 0, 0
        if relative_to_name:
            base_loc = db.get_location_by_name(relative_to_name)
            if base_loc:
                bx, by = base_loc['x'], base_loc['y']
                
                # Directional offsets
                offset = self.grid_size
                directions = {
                    "north": (0, offset),
                    "south": (0, -offset),
                    "east": (offset, 0),
                    "west": (-offset, 0),
                    "northeast": (offset, offset),
                    "northwest": (-offset, offset),
                    "southeast": (offset, -offset),
                    "southwest": (-offset, -offset)
                }
                
                dx, dy = directions.get(direction.lower() if direction else "", (random.randint(-offset, offset), random.randint(-offset, offset)))
                x, y = bx + dx, by + dy
        else:
            # If it's the first location, put it at 0,0
            all_locs = db.get_all_locations()
            if all_locs:
                # Find a spot near the center of gravity or just random offset from the first one
                base = all_locs[0]
                x = base['x'] + random.randint(-self.grid_size, self.grid_size)
                y = base['y'] + random.randint(-self.grid_size, self.grid_size)

        # Detect biome via LLM
        biome = self.detect_biome(name, description)
        
        loc_id = db.add_location(name, description, x, y, biome)
        return loc_id

    def detect_biome(self, name, description):
        """
        Uses the LLM to categorize the location into a biome type.
        """
        prompt = f"""
[SYSTEM: You are the Cartographer. Categorize the following location into one of these biomes: 
'Forest', 'Mountain', 'Plain', 'Desert', 'Tundra', 'Swamp', 'Ocean', 'Urban', 'Underground', 'Space'.

LOCATION: {name}
DESCRIPTION: {description}

REPLY ONLY WITH THE BIOME NAME.]
"""
        biome = ""
        for chunk in llm.generate_story_segment(prompt):
            biome += chunk
        return biome.strip()

    def move_entity(self, entity_type, entity_id, location_name):
        """
        Moves a character or player to a named location.
        """
        loc = db.get_location_by_name(location_name)
        if not loc:
            # If location doesn't exist, we might need to create it (though usually handled by identify_location)
            return False
            
        db.set_entity_position(entity_type, entity_id, loc['id'])
        return True

if __name__ == "__main__":
    print("Testing World Engine...")
    we = WorldEngine()
    loc_id = we.resolve_new_location("The Dusty Tavern", "A creaky old building full of travelers.")
    print(f"Created location {loc_id} at (0,0)")
    
    loc_id2 = we.resolve_new_location("The Whispering Woods", "A dark and scary forest.", "The Dusty Tavern", "North")
    print(f"Created location {loc_id2} relative to Tavern.")
