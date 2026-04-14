# Autonomous Research Implementation Plan

## Phase 1: Search Module
- [x] Create `researcher.py`.
- [x] Implement a function to perform a web search (using `duckduckgo_search`).
- [x] Build the "Idea Extractor" prompt to distill search results into narrative hooks.

## Phase 2: Director Integration
- [ ] Update `director.py` to include a `check_for_novelty()` function.
- [ ] Implement logic to trigger `researcher.search_for_inspiration()` when the novelty threshold is met.

## Phase 3: Lore Integration
- [ ] Automatically save discovered ideas into the SQLite `lore` and `plot_threads` tables.
- [ ] Ensure the LLM receives these new facts via the `curator.py` module.
