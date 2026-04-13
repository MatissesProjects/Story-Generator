# Narrative Orchestration Implementation Plan

## Phase 1: Continuation Logic
- [x] Update `parser.py` to detect "continue" intents.
- [x] Modify `server.py` to trigger a specific "Continuation Prompt" when the intent is detected.

## Phase 2: The Director Agent
- [x] Create `director.py`.
- [x] Implement the `evaluate_state()` function that checks current progress against `Plot_Threads`.
- [x] Inject `[DIRECTOR_INSTRUCTION]` into the `llm.py` prompt assembly.

## Phase 3: Persona Conditioning
- [x] Update the prompt template to include character-specific constraint blocks.
- [x] Ensure the TTS voice selection remains synced with the Persona Block.
