# Semantic Memory Specification

## Objective
Upgrade the context retrieval system from keyword-based matching to semantic similarity using a local Vector Database. This allows the story engine to "remember" relevant facts even when not explicitly named.

## Requirements
- **Local Embedding Engine**: Integrate a local model (e.g., `sentence-transformers` via `ollama` or `all-MiniLM-L6-v2`) to convert text into vector embeddings.
- **Vector DB Storage**: Implement a local vector store (e.g., **ChromaDB**, **FAISS**, or **SQLite-vss**) to index all character sheets, lore entries, and past major plot events.
- **Semantic Retrieval Loop**:
    1. Embed the current user input and the last 3 narrative turns.
    2. Query the Vector DB for the top-K most similar entries.
    3. Filter these results by a "Relevance Threshold" to prevent noise.
- **Hybrid Search**: Combine semantic results with exact keyword matches from the primary SQLite DB (e.g., specific character names should always trigger their sheets).

## Strategic Value
This enables "Atmospheric Recall." If the player enters a "cave," the system will recall lore about "underground darkness" or "ancient echoes" without the player needing to specify a named location.
