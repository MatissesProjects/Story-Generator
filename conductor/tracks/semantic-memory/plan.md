# Semantic Memory Implementation Plan

## Phase 1: Embedding Integration
- [ ] Install `chromadb` and `sentence-transformers`.
- [ ] Create `memory_engine.py` to handle text-to-vector conversion.
- [ ] Implement a script to embed all existing `Lore` and `Characters` from SQLite.

## Phase 2: Retrieval Logic
- [ ] Modify `curator.py` to perform a similarity search in ChromaDB.
- [ ] Implement the "Relevance Threshold" logic.
- [ ] Update the prompt builder to include the top 3 semantic matches.

## Phase 3: Validation
- [ ] Test with a query that doesn't use exact keywords (e.g., "Tell me about the darkness") and verify it pulls lore about "The Abyss."
