import db
import llm
import json
import random

class WorldEngine:
    def __init__(self):
        self.grid_size = 100 # Arbitrary unit

    async def resolve_new_location(self, name, description, relative_to_name=None, direction=None):
        """
        Determines where a new location should be placed on the 2D map and detects its physical properties.
        """
        existing = db.get_location_by_name(name)
        if existing:
            # Update last visited
            db.set_entity_position("player", 0, existing['id'])
            return existing['id']

        x, y = 0, 0
        base_elevation = 0
        if relative_to_name:
            base_loc = db.get_location_by_name(relative_to_name)
            if base_loc:
                bx, by = base_loc['x'], base_loc['y']
                base_elevation = base_loc.get('elevation', 0)
                
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
                base = all_locs[0]
                x = base['x'] + random.randint(-self.grid_size, self.grid_size)
                y = base['y'] + random.randint(-self.grid_size, self.grid_size)
                base_elevation = base.get('elevation', 0)

        # Detect physical properties via LLM
        props = await self.detect_physical_properties(name, description, base_elevation)
        
        loc_id = db.add_location(
            name, description, x, y, 
            biome_type=props.get('biome', 'Plain'),
            elevation=props.get('elevation', 0),
            climate=props.get('climate', 'Temperate')
        )
        return loc_id

    async def detect_physical_properties(self, name, description, base_elevation):
        """
        Uses the LLM to categorize the location's biome, elevation, and climate.
        """
        prompt = f"""
[SYSTEM: You are the Physical World Architect. Analyze the following location and determine its physical properties.

LOCATION: {name}
DESCRIPTION: {description}
NEARBY ELEVATION: {base_elevation}

Reply ONLY with a JSON object:
{{
    "biome": "Forest/Mountain/Plain/Desert/Tundra/Swamp/Ocean/Urban/Underground/Space",
    "elevation": -100 to 1000 (relative to sea level 0),
    "climate": "Arctic/Temperate/Tropical/Arid/Volcanic/Void",
    "connectivity_score": 0.0 to 1.0 (How easy is it to travel through?)
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
            return json.loads(clean_json)
        except Exception:
            return {"biome": "Plain", "elevation": 0, "climate": "Temperate", "connectivity_score": 0.5}

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
