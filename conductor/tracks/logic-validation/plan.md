# Logic Validation Implementation Plan

## Phase 1: Intent Parsing
- [ ] Create `validator.py`.
- [ ] Implement a fast Ollama call with a strict JSON schema for intent classification.

## Phase 2: World Rule Check
- [ ] Create a "Rules Engine" that queries SQLite for "World Flags."
- [ ] Implement a `check_possibility(action, context)` function.

## Phase 3: Interception
- [ ] Modify `main.py` and `server.py` to short-circuit the generation loop if a logical violation is found.
