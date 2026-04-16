# Robust Testing Implementation Plan

## Phase 1: Test Infrastructure
- [x] Create `tests/` directory structure: `tests/unit`, `tests/integration`, `tests/adversarial`.
- [x] Implement `tests/conftest.py` with standard mocks for `llm.async_generate_full_response` and DB connections.
- [x] Add `pytest` and `pytest-asyncio` to the project requirements.

## Phase 2: Adversarial Unit Tests
- [x] **Social Engine**: Implement the "Substring Collision" and "Multi-Character Betrayal" tests.
- [x] **World Engine**: Implement "Coordinate Collision" and "Orphaned Relative" tests.
- [x] **Validator**: Implement "Inventory Depletion" and "Lore Violation" tests.

## Phase 3: Robust Parsing & Fail-Safes
- [ ] Refactor JSON parsing in all modules to use a central `utils.safe_parse_json()` helper.
- [ ] Transition `validator.py` and `director.py` to "Fail-Closed" logic.
- [ ] Implement automated retries for LLM parsing failures.

## Phase 4: Integration & Regression
- [ ] Create a "Golden Turn" integration test that runs a full Turn 1 through Turn 5 sequence with mocked results.
- [ ] Automate `canon_checker` and `foreshadowing` validation in the test suite.
- [ ] Add a script to run all tests and generate a coverage report.
