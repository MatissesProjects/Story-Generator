# System Refinement & Polish Implementation Plan

## Phase 1: Narrative Version Control
- [x] **Snapshot Schema**: Update `schema.sql` with `snapshots` and `story_heads` tables.
- [x] **Commit Logic**: Implement `db.commit_snapshot()` to save the full state after each turn.
- [x] **Branching API**: Implement `checkout_snapshot(id)` in `db.py`.

## Phase 2: Visual Timeline UI
- [x] **Timeline View**: Create a vertical history in the UI sidebar showing story turns.
- [x] **Checkout Logic**: Add buttons to switch the story state to previous turns.

## Phase 3: Inventory & Stats
- [x] Update `schema.sql` with `inventory` and `entity_stats`.
- [x] Add an "Inventory" and "Stats" section to the sidebar.
- [x] Update the `validator.py` prompt to consider character inventory and stats.

## Phase 4: Model Optimization
- [x] Update `config.py` to support `FAST_MODEL` and `CREATIVE_MODEL`.
- [x] Update all logic/analysis modules to use the `FAST_MODEL` for performance.
- [x] Update `llm.py` to route creative storytelling to the `CREATIVE_MODEL`.
