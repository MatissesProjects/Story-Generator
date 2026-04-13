# Episodic Summarization Implementation Plan

## Phase 1: History Buffer
- [ ] Create a `memory_log` table in SQLite to track every turn of raw text.
- [ ] Implement a `get_recent_history(n)` function.

## Phase 2: Summarization Loop
- [ ] Create `summarizer.py`.
- [ ] Implement a trigger that runs every 10 turns.
- [ ] Store the resulting "Narrative Seed" in a `global_state` table.

## Phase 3: Integration
- [ ] Update `curator.py` to prepend the "Narrative Seed" to every prompt.
