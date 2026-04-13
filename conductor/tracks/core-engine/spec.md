# Core Engine & Memory Specification

## Objective
Establish the foundational interaction loop with the local Ollama instance and build a SQLite database to persistently store story state, character sheets, and lore.

## Requirements
- Python script to communicate with Ollama's local API.
- SQLite schema defining tables for `Characters`, `Lore`, `Plot_Threads`, and `Timeline`.
- Basic CLI or script interface to input commands and receive text output.