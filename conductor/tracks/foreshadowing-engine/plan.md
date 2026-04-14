# Foreshadowing Engine Implementation Plan

## Phase 1: Seed Extraction
- [ ] Update `schema.sql` with the `foreshadowed_elements` table.
- [ ] Create an LLM "Seed Extractor" that scans Assistant responses for minor, interesting details that aren't yet plot threads.

## Phase 2: Payoff Logic
- [ ] Update `director.py` to occasionally (e.g., every 20 turns) prioritize a foreshadowed element for payoff.
- [ ] Implement a `payoff_element(id)` function to mark seeds as resolved.

## Phase 3: Visualization
- [ ] Add a "Foreshadowing Log" (hidden by default) to the debug console to track active seeds.
