# Context Management Specification

## Objective
Implement a "Context Curator" that filters the SQLite database based on the current scene or dialogue, injecting only relevant facts into the LLM prompt to minimize token usage and maintain consistency.

## Requirements
- A mechanism to analyze the current user input or recent history for keywords or semantic relevance.
- A query builder to extract related `Characters`, `Lore`, and active `Plot_Threads` from SQLite.
- A prompt assembly function that prefixes the LLM request with the retrieved context.