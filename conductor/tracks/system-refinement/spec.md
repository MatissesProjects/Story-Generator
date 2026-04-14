# System Refinement & Polish Specification

## Objective
Elevate the Story Generator from a prototype to a polished narrative tool by implementing advanced UX features, robust state management, and refined AI behaviors.

## Requirements
- **Git-like Narrative Branching**:
    - **Snapshots**: Every turn is treated as a "commit" containing the full state (Seed, History, Location, Stats).
    - **Parenting**: Each snapshot points to its parent ID, allowing for a tree-based history.
    - **Branches**: Users can create named branches (e.g., "The Dark Path," "The Merciful Choice") from any snapshot in the timeline.
    - **Checkout/Rewind**: Instantly switch the "Active Head" to any previous snapshot or a different branch.
- **State Persistence (Save/Load)**:
    - Implement named "Story Universes."
    - A `snapshots` table in SQLite stores the entire narrative context for that specific moment in time.
- **Inventory & Entity Stats**:
    - Track "Discovered Items" and "Character Health/Wealth" in the DB.
    - Inject these stats into the `validator.py` logic (e.g., cannot buy a sword without gold).
- **Multi-Model Orchestration**:
    - Optimize model usage: Use a very small/fast model for `validator` and `parser`, and a large/creative model for `llm.generate_story_segment`.
- **Advanced Audio (Piper Emotion)**:
    - Fine-tune voice selection based on the `mood` detected by the `music_orchestrator`.

## Strategic Value
Refinement ensures the tool is reliable and feature-complete for end-users. Narrative branching specifically increases the "game-like" quality, allowing for exploration of alternate realities within the same world lore.
