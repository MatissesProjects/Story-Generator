# Pacing Director Implementation Plan

## Phase 1: Directive Schema
- [x] Update `llm.py` to handle a `pacing_directive` parameter.
- [x] Create specialized prompt templates for each pacing category.

## Phase 2: Automated Pacing
- [x] Implement background state management for pacing in `server.py`.

## Phase 3: UI Controls
- [x] Add a "Narrative Pacing" selector to the Web UI.
- [x] Synchronize pacing state via WebSockets.
