# Narrative Orchestration Implementation Plan

## Phase 1: Continuation Logic
- [ ] Update `parser.py` to detect "continue" intents.
- [ ] Modify `server.py` to trigger a specific "Continuation Prompt" when the intent is detected.

## Phase 2: The Director Agent
- [ ] Create `director.py`.
- [ ] Implement the `evaluate_state()` function that checks current progress against `Plot_Threads`.
- [ ] Inject `[DIRECTOR_INSTRUCTION]` into the `llm.py` prompt assembly.

## Phase 3: Persona Conditioning
- [ ] Update the prompt template to include character-specific constraint blocks.
- [ ] Ensure the TTS voice selection remains synced with the Persona Block.
