# Adventure Arcs Implementation Plan

## Phase 1: Arc Loader
- [ ] Create `static/arcs/` directory for template files.
- [ ] Implement `load_arc(filename)` in `db.py` to populate the initial lore and plot threads.

## Phase 2: Milestone Manager
- [ ] Update `director.py` to track the current "Chapter" and "Active Milestone."
- [ ] Create an LLM prompt to detect if a milestone's conditions have been met.

## Phase 3: Chapter Transitions
- [ ] Update `summarizer.py` to perform a "Chapter Summary" when an arc milestone is reached.
- [ ] Add visual "Chapter Complete" notifications to the UI.
