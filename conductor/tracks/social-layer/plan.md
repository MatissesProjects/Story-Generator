# Character Relationship Graph Implementation Plan

## Phase 1: Social Database
- [x] Update `schema.sql` with `relationships` and `interaction_log`.
- [x] Create `social_engine.py` to calculate relationship deltas based on turn outcomes.

## Phase 2: Social Prompting
- [x] Update `director.get_persona_blocks()` to include relationship descriptors.
- [x] Implement an LLM "Social Analyzer" in `social_engine.py` that runs after each turn.

## Phase 3: Graph Visualization
- [x] Add a "Social Standing" list to the frontend showing Trust, Fear, and Affection scores.
