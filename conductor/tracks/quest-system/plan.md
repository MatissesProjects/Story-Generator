# Quest System Implementation Plan

## Phase 1: Quest Foundation
- [x] Update `schema.sql` with `quests` and `quest_objectives` tables.
- [x] Create quest management functions in `db.py`.
- [x] Implement `get_active_quests()` for prompt injection.

## Phase 2: Curator Integration
- [x] Modify `curator.py` to include active quest details in the "Facts" block as "Active Leads".
- [x] Update `director.py` to evaluate quest progress after each turn and provide "Gentle Suggestions".

## Phase 3: Quest UI
- [x] Add a "Quest Log" component to the frontend sidebar.
- [x] Implement WebSocket events for `quest_update` and state syncing.
