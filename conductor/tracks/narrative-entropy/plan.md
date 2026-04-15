# 🗺️ Implementation Plan: Narrative Entropy

## Phase 1: Relationship Decay 📉
- [ ] Create `entropy_engine.py` with `decay_relationships()` function.
- [ ] Add `decay_relationships()` to `simulation_manager.py` tick logic.
- [ ] Implement decay math: move values towards 0 slightly every N ticks.

## Phase 2: Lore Duels (Conflict Resolution) ⚔️
- [ ] Update `canon_checker.py` to include `resolve_contradiction(claim, lore)`.
- [ ] Use the LLM to decide the outcome: Retcon (update DB), Unreliable Narrator (add note to history), or World Change (add new lore explaining the change).
- [ ] Integrate into `server.py`'s post-generation tasks.

## Phase 3: Lore Volatility 🌪️
- [ ] Add a chance for minor lore facts to mutate slightly during simulation ticks to simulate rumors.
- [ ] Ensure core facts don't mutate too quickly.

## Phase 4: Verification 🧪
- [ ] Create `test_entropy.py`.
- [ ] Verify relationship drift and contradiction resolution logic.
