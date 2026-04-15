# 🤖 Track: Proactive NPC Agency

## Overview
Move NPCs from reactive, player-dependent entities to proactive, goal-oriented agents with internal motivations ("Will"). NPCs will now have "Needs" that drive them to perform actions, move between locations, and interact with each other independently of the player.

## Core Objectives
- **Motivation System (Needs)**: Implement internal meters for NPCs: *Social*, *Ambition*, *Safety*, and *Resources*.
- **Utility AI / GOAP**: A decision-making engine that selects the best action to satisfy the NPC's most pressing need.
- **Autonomous Movement**: NPCs can decide to leave their current location and travel to another on the `world_engine` grid.
- **Inter-NPC Socializing**: NPCs can form and change relationships with each other, not just the player.
- **Task Persistence**: NPCs maintain a "Current Task" state across simulation ticks.

## Functional Requirements
1. **Agency Engine**: A new module `agency_engine.py` to calculate the "Next Best Action" for every active NPC.
2. **Needs Persistence**: Update `db.py` and `schema.sql` to store NPC motivation values and current goals.
3. **Tick Integration**: Hook the Agency Engine into `simulation_manager.py` so NPC logic runs during every global tick.
4. **NPC Activity Log**: A way to report autonomous NPC actions to the `simulation_history`.

## Dependencies
- `db.py`: For storing NPC state.
- `world_engine.py`: For handling NPC movement between grid coordinates.
- `simulation_manager.py`: For triggering the agency logic.
- `social_engine.py`: For calculating the outcomes of NPC-NPC interactions.
