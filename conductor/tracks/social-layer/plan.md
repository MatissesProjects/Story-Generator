# Character Relationship Graph Implementation Plan

## Phase 1: Social Database
- [ ] Update `schema.sql` with `relationships` and `interaction_log`.
- [ ] Create `social_engine.py` to calculate relationship deltas based on turn outcomes.

## Phase 2: Social Prompting
- [ ] Update `director.get_persona_blocks()` to include relationship descriptors (e.g., "Trusts you deeply," "Secretly resents Malakar").
- [ ] Implement an LLM "Social Analyzer" that runs after dialogue to update scores.

## Phase 3: Graph Visualization
- [ ] Add a "Social Map" tab to the frontend using a force-directed graph library (e.g., D3.js or a simple canvas implementation).
