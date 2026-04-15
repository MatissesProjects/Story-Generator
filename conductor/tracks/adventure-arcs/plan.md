# Adventure Arcs Implementation Plan

## Phase 1: Arc Loader
- [x] Create `static/arcs/` directory for template files.
- [x] Implement `set_active_arc()` and `get_active_arc()` in `db.py`.

## Phase 2: Milestone Manager
- [x] Update `director.py` to track the current "Chapter" and "Active Milestone" via `evaluate_milestone_progress`.
- [x] Integrate milestone detection into the main turn loop in `server.py`.

## Phase 3: Chapter Transitions
- [x] Update the Web UI to display the current Arc title and Milestone description.
- [x] Trigger automatic narrative summarization on chapter transitions.
