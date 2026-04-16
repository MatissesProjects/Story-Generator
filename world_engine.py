import db
import llm
import json
import random
import config
import utils

class WorldEngine:
    def __init__(self):
        self.grid_size = 100 # Arbitrary unit

    async def resolve_new_location(self, name, description, relative_to_name=None, direction=None):
        """
        Determines where a new location should be placed on the 2D map and detects its physical properties.
        Prevents spatial collisions by jittering if a spot is taken.
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
                base_elevation = base_loc['elevation'] if 'elevation' in base_loc.keys() else 0
                
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
            # If it's not the first location, put it relative to something existing
            all_locs = db.get_all_locations()
            if all_locs:
                base = all_locs[0]
                x = base['x'] + random.randint(-self.grid_size, self.grid_size)
                y = base['y'] + random.randint(-self.grid_size, self.grid_size)
                base_elevation = base['elevation'] if 'elevation' in base.keys() else 0

        # Detect physical properties via LLM
        props = await self.detect_physical_properties(name, description, base_elevation)

        # SPATIAL COLLISION CHECK: Retry until a free spot is found
        max_attempts = 10
        loc_id = None
        for attempt in range(max_attempts):
            loc_id = db.add_location(
                name, description, x, y, 
                biome_type=props.get('biome', 'Plain'),
                elevation=props.get('elevation', 0),
                climate=props.get('climate', 'Temperate')
            )
            if loc_id:
                break
                
            # Jitter and try again
            x += random.randint(-10, 10)
            y += random.randint(-10, 10)
            
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
        result = utils.safe_parse_json(response)
        if result:
            return result
        return {"biome": "Plain", "elevation": 0, "climate": "Temperate", "connectivity_score": 0.5}

    def move_entity(self, entity_type, entity_id, location_name):
        """
        Moves a character or player to a named location.
        """
        loc = db.get_location_by_name(location_name)
        if not loc:
            return False
            
        db.set_entity_position(entity_type, entity_id, loc['id'])
        return True

if __name__ == "__main__":
    import asyncio
    async def test():
        print("Testing World Engine...")
        we = WorldEngine()
        loc_id = await we.resolve_new_location("The Dusty Tavern", "A creaky old building full of travelers.")
        print(f"Created location {loc_id} at (0,0)")
    
    asyncio.run(test())
