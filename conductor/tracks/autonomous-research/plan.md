# Autonomous Research Implementation Plan

## Phase 1: Search Module
- [x] Create `researcher.py`.
- [x] Implement a function to perform a web search (using `duckduckgo_search`).
- [x] Build the "Idea Extractor" prompt to distill search results into narrative hooks.

## Phase 2: Director Integration (Refined)
- [x] Update `director.py` to include a `check_narrative_gaps()` function that analyzes history and plot threads.
- [x] Implement `researcher.optimize_query()` which uses the LLM to transform simple themes into high-signal search queries.
- [x] Replace the random turn-based research with "Director-triggered" missions.

## Phase 3: Lore & Entity Injection
- [x] Automatically save discovered ideas into the SQLite `lore` and `plot_threads` tables. (Implemented)
- [x] Integrate the research pipeline into the main `server.py` loop.
- [x] Ensure the LLM receives these new facts via the `curator.py` module.
