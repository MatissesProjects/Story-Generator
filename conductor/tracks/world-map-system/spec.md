# World Map System Specification

## Objective
Create a persistent geographical representation of the story world. This tracks where characters are and allows the player to visualize the "distance" and "relationship" between locations.

## Requirements
- **Geography DB**: A `Locations` table in SQLite tracking coordinates (X, Y), region types, and connections (roads/paths).
- **Location Tracking**: Store the current coordinates of the `Player` and key `NPCs`.
- **Procedural Mapping**: 
    - Use the LLM to generate "Map Metadata" when new locations are discovered via exploration.
    - Generate visual map tiles or a full world map using the `vision.py` engine.
- **Interactive Map UI**:
    - A dedicated tab or modal in the frontend showing the world map.
    - Icons representing character positions and discovered landmarks.

## Strategic Value
The map turns a series of scenes into a coherent *world*. It provides a sense of scale and prevents geographical hallucinations (e.g., "the mountains are to the north, then suddenly to the south").
