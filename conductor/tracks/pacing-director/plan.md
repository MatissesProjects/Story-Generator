# Pacing Director Implementation Plan

## Phase 1: Directive Schema
- [ ] Update `llm.py` to handle a `pacing_directive` parameter.
- [ ] Create specialized prompt templates for each pacing category.

## Phase 2: Automated Pacing
- [ ] Update `director.py` to suggest pacing changes based on `check_narrative_gaps()` (e.g., if too much dialogue, suggest Action).

## Phase 3: UI Controls
- [ ] Add a "Narrative Tempo" widget to the Web UI.
- [ ] Display the current pacing mode in the status indicator.
