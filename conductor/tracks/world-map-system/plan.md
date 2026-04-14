# World Map System Implementation Plan

## Phase 1: Coordinate Logic
- [ ] Create the `locations` table in SQLite.
- [ ] Implement a `move_to(location)` function that updates character coordinates.

## Phase 2: Map Discovery
- [ ] Build a "Cartographer" module to generate coordinates and connections for new research-injected locations.
- [ ] Implement location-to-location pathfinding logic.

## Phase 3: Visual Map Frontend
- [ ] Create a canvas-based map viewer in the frontend.
- [ ] Implement "Fog of War" (only show discovered locations).
- [ ] Use Stable Diffusion to generate "Location Icons" or "Region Tiles."
