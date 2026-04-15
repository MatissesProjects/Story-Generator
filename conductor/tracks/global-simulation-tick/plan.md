# 🗺️ Implementation Plan: Global Simulation Tick

## Phase 1: Persistence & Foundation ⏳
- [ ] Update `schema.sql` and `db.py` to support `world_time` and `simulation_log`.
- [ ] Create `simulation_manager.py` with a basic `trigger_tick()` function.
- [ ] Hook the `trigger_tick()` into `server.py` (running every N player turns).

## Phase 2: System Integration ⚙️
- [ ] Integrate `world_engine`: Advance weather patterns and resource depletion.
- [ ] Integrate `social_engine`: Implement relationship decay and group loyalty shifts.
- [ ] Add "Hidden Events" logic: LLM generates background events (e.g., "A plague starts in the North").

## Phase 3: Player Feedback (Rumors) 🗣️
- [ ] Update `curator.py` to include recent high-impact global events in the prompt context.
- [ ] Implement a "Rumor Mill" where NPCs can mention things that happened during the simulation tick.

## Phase 4: Scaling & Optimization 🚀
- [ ] Move the tick to a background task in `server.py` to prevent blocking the generation.
- [ ] Implement "Level of Detail" (LOD) for simulation: More detail near the player, less detail far away.
