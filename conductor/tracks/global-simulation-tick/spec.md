# 🌍 Track: Global Simulation Tick

## Overview
Implement a central simulation loop that advances world time and triggers global events independently of the player's immediate dialogue. This creates a "Living World" where consequences unfold across the entire map.

## Core Objectives
- **Time Progression**: Implement a `world_time` counter in the database.
- **System Synchronization**: Coordinate updates across `world_engine`, `social_engine`, and `economy_engine` (future).
- **Background Events**: Generate major narrative shifts that the player only hears about via rumors or discovery.
- **Consequence Chains**: Ensure that an action in one location can ripple across the map after several ticks.

## Functional Requirements
1. **The Tick Manager**: A new module `simulation_manager.py` that handles the execution of the global loop.
2. **Scheduled Updates**: 
   - Every 1 Tick: Time advancement.
   - Every 5 Ticks: Local faction movement and resource shifts.
   - Every 20 Ticks: Major weather/climate changes.
3. **Internal Log**: A `simulation_history` table to track what changed while the player was elsewhere.

## Dependencies
- `db.py`: For persistence of world time and global state.
- `world_engine.py`: For spatial updates.
- `social_engine.py`: For NPC group shifts.
