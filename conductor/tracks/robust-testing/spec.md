# Robust Testing Specification

## Objective
Ensure the long-term stability and logical consistency of the Story Generator by moving beyond "happy path" manual testing toward an automated, adversarial testing suite that targets complex edge cases and LLM failure modes.

## Core Focus Areas

### 1. Social Layer Integrity
- **Collision Detection**: Prevent social updates for characters with similar names (e.g., "Al" vs "Alice").
- **Multi-Entity Interactions**: Verify the engine's ability to process complex interactions involving 3+ characters correctly.
- **Pronoun & Contextual Resolution**: Test how the engine handles ambiguous references in LLM-generated dialogue.

### 2. World Engine & Spatial Consistency
- **Coordinate Collision**: Prevent two locations from occupying the same `(x, y)` coordinates.
- **Relativity Robustness**: Ensure new locations are correctly anchored to existing ones, with sensible fallbacks for missing parents.
- **Pathfinding Validation**: Verify that paths between locations are traversable and logically sound.

### 3. Logical Validation (Validator & DiceMaster)
- **Constraint Enforcement**: Verify that the `validator` strictly respects inventory and lore constraints.
- **Fail-Safe Audit**: Transition logic from "Fail-Open" (allowing invalid actions on error) to "Fail-Closed" (blocking actions on error) with clear user feedback.
- **Deterministic Dice**: Mock the DiceMaster to ensure mechanical outcomes are predictable and repeatable during testing.

### 4. LLM Robustness & Parsing
- **Malformed JSON Handling**: Ensure every module can handle non-JSON or partial-JSON responses from the LLM without crashing.
- **Hallucination Detection**: Implement automated checks for "impossible" claims in generated story segments.

## Success Metrics
- 100% pass rate for "Adversarial Suite" (edge cases).
- Automated regression testing for all reported "Logical Contradiction" bugs.
- Implementation of a dedicated `tests/` directory structure separating unit and integration tests.
