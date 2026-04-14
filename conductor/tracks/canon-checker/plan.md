# Canon Checker Implementation Plan

## Phase 1: Claim Extraction
- [x] Create an LLM prompt that extracts "World-Building Facts" from a given block of text.
- [x] Implement a `validate_canon(text)` function in `canon_checker.py`.

## Phase 2: Knowledge Retrieval
- [x] Update `curator.py` to provide a "Canon Reference" for the validator.
- [x] Implement a similarity threshold/LLM arbiter for determining if two facts are contradictory.

## Phase 3: Loop Feedback
- [ ] Integrate with `server.py` to trigger a regeneration if a high-confidence violation is detected.
