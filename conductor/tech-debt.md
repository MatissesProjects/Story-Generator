# Technical Debt & Refactoring Tracker

This document tracks identified architectural issues, performance bottlenecks, and technical debt across the Story-Generator project.

## Priority 1: Concurrency & Performance Bottlenecks (High)
*   [x] **Blocking Vision Engine**: Wrapped PyTorch inference in `asyncio.to_thread` and implemented concurrency locks for shared state.
*   [x] **Synchronous Database Calls**: Wrapped DB reads in `asyncio.to_thread` and implemented thread-local persistent connections.

## Priority 2: Architectural Monoliths (Medium)
*   [x] **The "God Object" (`server.py`)**: Extracted the core "Turn Loop" into `turn_orchestrator.py`.
*   [x] **The Frontend Giant (`static/app.js`)**: Modularized the massive script into 8 domain-specific files.

## Priority 3: Database Inefficiencies (Medium)
*   [x] **Connection Thrashing**: Implemented a persistent connection manager using `threading.local`.
*   [x] **N+1 Queries**: Optimized `get_active_quests` using batch queries.

## Priority 4: Logic Duplication & Bugs (Low)
*   [x] **Redundant JSON Cleaning**: Consolidated all LLM JSON parsing into `utils.safe_parse_json`.
*   [x] **Incomplete Features**: Integrated NPC Agency and Simulation events into the main narrative and Director instructions.
*   [x] **Hardened Robustness**: Added comprehensive `try...except` blocks around all external API and I/O interaction points to prevent system-wide crashes.
