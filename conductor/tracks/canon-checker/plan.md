# Canon Checker Implementation Plan

## Phase 1: Claim Extraction
- [ ] Create an LLM prompt that extracts "World-Building Facts" from a given block of text.
- [ ] Implement a `validate_canon(text)` function.

## Phase 2: Knowledge Retrieval
- [ ] Update `curator.py` to provide a "Canon Reference" for the validator.
- [ ] Implement a similarity threshold for determining if two facts are contradictory.

## Phase 3: Loop Feedback
- [ ] Integrate with `server.py` to trigger a regeneration if a high-confidence violation is detected.
