# DiceMaster Module Implementation Plan

## Phase 1: Hidden Roll Engine
- [ ] Create `dicemaster.py` with `roll_d20()` and `evaluate_check(roll, dc)` functions.
- [ ] Implement `determine_dc(action, context)` using an LLM call to set difficulty based on world lore.

## Phase 2: Orchestration (Post-Validation)
- [ ] Update `server.py`: After logic validation, if the intent is 'ACTION', perform a hidden check.
- [ ] Inject the `[MECHANICAL RESULT]` into the `llm.generate_story_segment` prompt.
- [ ] Update `parser.py` to identify if the user *explicitly* wants to see the roll (e.g., "> CHECK Athletics").

## Phase 3: UI Feedback (Subtle)
- [ ] Implement a subtle visual indicator in the Web UI for Success/Failure.
- [ ] Log the hidden math to the "Debug Console" so the user can see it if they wish.
