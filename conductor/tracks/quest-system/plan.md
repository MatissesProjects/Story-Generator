# Quest System Implementation Plan

## Phase 1: Quest Foundation
- [ ] Update `schema.sql` with `quests` and `quest_objectives` tables.
- [ ] Create `quest_manager.py` to handle quest CRUD operations.
- [ ] Implement `get_active_quests()` for prompt injection.

## Phase 2: Curator Integration
- [ ] Modify `curator.py` to include active quest details in the "Facts" block.
- [ ] Update `director.py` to evaluate quest progress after each turn.

## Phase 3: Quest UI
- [ ] Add a "Quest Log" component to the frontend sidebar.
- [ ] Implement WebSocket events for `quest_update` and `objective_complete`.
