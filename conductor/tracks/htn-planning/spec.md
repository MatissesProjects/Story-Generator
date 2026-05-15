# Specification: HTN Planning for Narrative Intelligence

## 1. Overview
The current narrative system uses linear "Adventure Arcs" with fixed milestones. While robust, this is reactive and brittle when players deviate. We will replace this with a **Hierarchical Task Network (HTN)** planner. This allows the story to be defined as a set of high-level goals that the system actively tries to achieve through NPC actions and environmental shifts.

## 2. Core Concepts

### 2.1 The World State
The planner will operate on a "Working Memory" snapshot derived from:
- `db.py`: Player inventory, NPC locations, quest status.
- `memory_engine.py`: Relevant lore and character relationships.

### 2.2 Tasks
- **Compound Tasks**: Abstract goals like `Heist`, `Investigation`, or `Assassination`.
- **Primitive Tasks (Operators)**: Atomic actions the engine can perform, such as `MoveNPC`, `ModifyInventory`, `TriggerEnvironmentEvent`, or `InjectDialogueInstruction`.

### 2.3 Methods
Logical rules that define how a Compound Task is decomposed into smaller tasks based on the current world state.
- *Example*: `Infiltrate` could decompose into `RecruitHelp` -> `SneakIn` OR `BribeGuard` -> `WalkIn` depending on player wealth and social ties.

## 3. Implementation Logic

### 3.1 Data Schema
We will need to store the active plan and its current progress in the database.
- `active_plan`: A JSON array of remaining primitive tasks.
- `domain_definitions`: A library of narrative methods.

### 3.2 The Planning Loop
1. **Appraise**: Gather the current world state.
2. **Plan**: Decompose the active high-level goal into a list of primitive tasks.
3. **Execute**: The Director takes the first primitive task and translates it into prompt instructions or DB updates.
4. **Re-plan**: If the world state changes significantly (due to player action), discard the current plan and generate a new one.

## 4. Integration Points
- `director.py`: Will become the "Plan Executor."
- `agency_engine.py`: Will receive "Sub-plans" for NPCs to execute.
- `server.py`: The turn loop will trigger a "Plan Validity Check" every turn.
