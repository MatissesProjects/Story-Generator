# DiceMaster Module Implementation Plan

## Phase 1: Roll Engine
- [ ] Create `dicemaster.py` to handle RNG and DC interpretation.
- [ ] Update `parser.py` to detect "Attempt" or "Action" keywords that imply a check.

## Phase 2: Orchestration
- [ ] Integrate `dicemaster` into the `server.py` turn loop.
- [ ] Modify the prompt to include: "[MECHANICAL RESULT: ROLL 12 vs DC 15 - FAILURE. Narrate the character getting caught.]"

## Phase 3: UI Integration
- [ ] Add a "Dice Overlay" to the frontend that triggers during checks.
- [ ] Display the roll history in the story area.
