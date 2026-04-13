# Narrative Orchestration Specification

## Objective
Implement a "Director Agent" that manages the overarching plot and handles autonomous story continuation (the "Continue" command).

## Requirements
- **The Director Loop**:
    - A secondary LLM process that runs every few turns to analyze the "State of the Story."
    - It compares the current scene to the `Plot_Threads` table in SQLite.
    - It generates "Director Instructions" (hidden prompts) to nudge the main LLM toward unresolved goals.
- **Autonomous Continuation ("Continue" Logic)**:
    - **Intent Detection**: The system must recognize "continue," "tell me more," or empty inputs as a request for narrative expansion rather than a player action.
    - **Narrative Momentum**: When a "continue" intent is detected, the prompt is modified to: *"The player is waiting. Describe the next sequence of events, focusing on atmospheric detail and character reaction. Do not wait for player input yet."*
- **Persona Conditioning**:
    - For every speaker detected in the current context, the Orchestrator must inject a strict **Persona Block** before the generation begins.
    - Format: `[SPEAKER: {Name}; TRAITS: {Traits}; CURRENT_MOOD: {Mood}; HIDDEN_GOAL: {Goal}]`.

## Strategic Value
Prevents the story from becoming reactive and aimless. The Director ensures the world feels "alive" and moving even when the player is passive.
