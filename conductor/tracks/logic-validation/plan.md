# Logic Validation Implementation Plan

## Phase 1: Intent Parsing
- [x] Create `validator.py`.
- [x] Implement a fast Ollama call with a strict JSON schema for intent classification and rule enforcement.

## Phase 2: World Rule Check
- [x] Use `curator` context facts to check actions against current world rules.
- [x] Implement logic to distinguish between possible and impossible actions.

## Phase 3: Interception
- [x] Modify `server.py` to short-circuit the generation loop if a logical violation is found.
