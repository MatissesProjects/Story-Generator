# Foreshadowing Engine Implementation Plan

## Phase 1: Seed Extraction
- [x] Update `schema.sql` with the `foreshadowed_elements` table.
- [x] Create an LLM "Seed Extractor" in `foreshadowing.py`.

## Phase 2: Payoff Logic
- [x] Update `director.py` (Integrated via `server.py` and `foreshadowing.py`) to occasionally prioritize a foreshadowed element for payoff.
- [x] Implement a `resolve_foreshadowing(id)` function.

## Phase 3: Visualization
- [x] Log foreshadowing events to the debug console.
