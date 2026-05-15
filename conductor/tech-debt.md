# Technical Debt & Refactoring Tracker

This document tracks identified architectural issues, performance bottlenecks, and technical debt across the Story-Generator project.

## Priority 1: Concurrency & Performance Bottlenecks (High)
*   [x] **Blocking Vision Engine**: The `vision.run_inference` method uses PyTorch for image generation. Although marked `async`, the inference call itself is synchronous and blocks the main Python `asyncio` event loop. This causes the server to hang, preventing new text chunks or WebSocket messages from being processed during generation.
    *   *Solution*: Wrap the PyTorch inference in `asyncio.to_thread`.
*   [x] **Synchronous Database Calls**: The main WebSocket loop makes many database calls (e.g., checking inventory, stats, quests) sequentially using the synchronous `sqlite3` module. This blocks the server briefly on every turn.
    *   *Solution*: Migrate the database layer to an async driver (like `aiosqlite`) or wrap operations in worker threads.

## Priority 2: Architectural Monoliths (Medium)
*   [x] **The "God Object" (`server.py`)**: At nearly 900 lines, the server file handles everything from WebSocket routing to story logic, validation, and phase orchestration.
    *   *Solution*: Break the "Turn Loop" logic into a separate `turn_orchestrator.py` module.
*   [ ] **The Frontend Giant (`static/app.js`)**: At over 1100 lines, this file handles DOM manipulation, WebSocket events, complex audio/visual queuing, and state management all in one place.
    *   *Solution*: Modularize into smaller files (e.g., `audio.js`, `ui.js`, `network.js`), maintaining vanilla JS if desired.

## Priority 3: Database Inefficiencies (Medium)
*   [ ] **Connection Thrashing**: `db.py` opens and closes a new SQLite connection for every single query via `query_db` / `execute_db`.
    *   *Solution*: Implement a connection pool or a persistent connection manager.
*   [ ] **N+1 Queries**: Functions like `get_active_quests` fetch the quests, then perform a separate query in a loop to fetch the objectives for each quest.
    *   *Solution*: Use `JOIN` queries or batch fetching to reduce the number of queries.

## Priority 4: Logic Duplication & Bugs (Low)
*   [ ] **Redundant JSON Cleaning**: `director.py`, `utils.py`, and `simulation_manager.py` all have custom, slightly varying logic for extracting and parsing JSON from LLM markdown outputs (e.g., stripping ` ```json `).
    *   *Solution*: Consolidate this into a single, robust function in `utils.py`.
*   [ ] **Incomplete Features**: `agency_engine.py` is partially implemented but lacks deep integration with the main narrative loop.
    *   *Solution*: fully integrate or remove if deprecated.
