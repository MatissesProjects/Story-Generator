# Pacing Director Specification

## Objective
Give the user/GM control over the narrative rhythm by enforcing specific "Pacing Directives" that influence the focus and length of LLM outputs.

## Requirements
- **Pacing Categories**:
    - **Introspective**: Focus on internal thoughts, memory, and emotion.
    - **Action-Packed**: High-tempo verbs, immediate threats, fast-paced dialogue.
    - **Mystery-Focused**: Focus on atmospheric detail, clues, and subtle hints.
    - **Dialogue-Heavy**: Focus on character interactions and verbal subtext.
- **Prompt Injection**: Injects a strict `[PACING_DIRECTIVE: {Type}]` instruction into the generator prompt.
- **Pacing Controls UI**: A slider or set of buttons in the frontend to change the current "Mood" of the narration.

## Strategic Value
Prevents the story from feeling "one-note." It allows the player to slow down for emotional moments or speed up for high-stakes sequences, much like a professional editor or DM.
