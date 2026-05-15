# Implementation Plan: HTN Planning

## Phase 1: Core Planner Engine
Build the generic HTN solver that can handle narrative methods and operators.

- [x] **Planner Class (`htn_engine.py`)**:
  - Implement a `solve(world_state, goal)` method.
  - Implement a recursive decomposition algorithm.
  - Add support for "Sensors" to pull from `db.py`.
- [x] **Narrative Domain Library (`htn_domains.py`)**:
  - Define the first narrative domain: `Mystery_Investigation`.
  - Define methods for "Find Clue", "Confront Suspect", "Reveal Truth".
- [x] **Unit Tests**:
  - Verify that the planner finds the correct sequence of actions for various world states.

## Phase 2: Database & State Integration
Connect the planner to the persistent story state.

- [x] **DB Updates (`db.py`)**:
  - Add tables for `active_narrative_plan` and `completed_tasks`.
- [x] **Plan Monitor**:
  - Create a utility to check if the current turn's text "satisfies" the requirements of the next primitive task.

## Phase 3: Director Orchestration
Replace the legacy Adventure Arc logic with the HTN output.

- [x] **Director Refactor (`director.py`)**:
  - Update `evaluate_state` to prioritize the current HTN task.
  - Generate "Director Instructions" specifically designed to nudge the story toward the task goal.
- [x] **Agency Integration**:
  - Allow NPCs to "pick up" HTN tasks (via Director Instructions).

## Phase 4: Verification
- [ ] **Stress Test**: Play a scenario where the player actively avoids the plot (e.g., leaving the city during a heist) and verify the HTN planner re-routes the narrative logically.
