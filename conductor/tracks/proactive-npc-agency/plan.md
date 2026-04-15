# 🗺️ Implementation Plan: Proactive NPC Agency

## Phase 1: Motivation & Persistence 🧱
- [ ] Update `schema.sql` and `db.py` to add NPC meters (`social`, `ambition`, `safety`, `resources`).
- [ ] Add `current_goal` and `current_task` columns to the `characters` table.
- [ ] Implement `init_npc_needs()` to provide reasonable defaults for new/existing characters.

## Phase 2: The Agency Engine (Will) 🧠
- [ ] Create `agency_engine.py`.
- [ ] Implement a **Need Decay** function: Needs should worsen every tick.
- [ ] Create a "Utility Score" calculator: Which action (Socialize, Seek Safety, Move, Work) has the highest payoff?
- [ ] Integrate with the LLM to generate specific "Autonomous Action Descriptions" (e.g., "Elara left for the Silver City to find herbs").

## Phase 3: Movement & Socialization 🚶‍♂️
- [ ] Implement autonomous movement: NPCs use `world_engine` to move to adjacent or target locations.
- [ ] Implement NPC-to-NPC social interactions: Update `social_engine` to handle relationships where neither party is the player.
- [ ] Update `simulation_history` to log these private NPC moments.

## Phase 4: Integration & Visibility 📡
- [ ] Hook `agency_engine.run_tick()` into `simulation_manager.py`.
- [ ] Update `curator.py` so the player "hears news" of what NPCs have been doing.
- [ ] (Optional) Update `app.js` to show NPC movement on the map visually.

## Phase 5: Verification 🧪
- [ ] Create `test_agency.py`.
- [ ] Verify that NPCs actually satisfy their needs over multiple ticks.
