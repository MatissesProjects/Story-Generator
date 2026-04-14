# System Refinement & Polish Implementation Plan

## Phase 1: Narrative Version Control
- [ ] **Snapshot Schema**: Update `schema.sql` with `snapshots` and `story_heads` tables.
- [ ] **Commit Logic**: Implement `world_engine.commit_snapshot()` to save the full state after each turn.
- [ ] **Branching API**: Implement `create_branch(name)` and `checkout_snapshot(id)` in `db.py`.

## Phase 2: Visual Timeline UI
- [ ] **Timeline View**: Create a vertical "Commit Graph" in the UI sidebar showing story turns.
- [ ] **Branch Manager**: Add buttons to create branches from previous turns.
- [ ] **Visual Diff**: Optionally show what changed in the "Seed" between two snapshots.

## Phase 3: Inventory & Stats
- [ ] Update `schema.sql` with `inventory` and `entity_stats`.
- [ ] Add an "Inventory" tab to the sidebar.
- [ ] Update the `validator.py` prompt to consider character inventory and stats.

## Phase 4: Model Optimization
- [ ] Update `config.py` to support `FAST_MODEL` and `CREATIVE_MODEL`.
- [ ] Update `llm.py` route requests based on task (Creative vs Logic).
