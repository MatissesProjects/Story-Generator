# World Map System Specification (Refined)

## Objective
Implement a persistent, procedurally-expanding geographical engine that tracks character movements, maintains spatial consistency, and provides a visual representation of the story world.

## Requirements
- **Spatial Database (SQLite)**:
    - `Locations` table: `id, name, description, x, y, biome_type, region_id`.
    - `Regions` table: `id, name, theme, security_level`.
    - `Paths` table: `from_id, to_id, distance, path_type (road, forest, sea)`.
    - `Entity_Positions`: `entity_type, entity_id, current_location_id, destination_id, travel_progress`.
- **The "Cartographer" Logic**:
    - **Coordinate Assignment**: When a new location is discovered, the LLM determines its relative position (e.g., "North of the Woods") and the system assigns X/Y coordinates on a 2D plane.
    - **Biome Influence**: The biome type (Tundra, Desert, Cyber-City) is passed to `vision.py` to ensure environment art matches the map.
- **Visual Map Engine**:
    - **Procedural Tile Generation**: Use Stable Diffusion to generate individual "Map Tiles" for different biomes.
    - **Dynamic Overlay**: A React/Vanilla JS Canvas component that renders the map, connections, and character icons.
    - **Fog of War**: Persistent tracking of "Discovered" vs "Hidden" sectors.
- **Movement & Travel**:
    - A `travel_to(destination)` system that calculates time based on distance and path type.
    - The Director Agent can trigger "Travel Encounters" while characters are in transit between nodes.

## Strategic Value
The World Map transforms the narrative from a series of disconnected rooms into a vast, navigable world. It enforces "Physical Truth"—if a character is in the North, they cannot suddenly appear in the South without traveling.
