# Episodic Summarization Specification

## Objective
Solve the "Context Window" limit by implementing a hierarchical memory system that periodically compresses old history into compact summaries.

## Requirements
- **Episodic Window**: Maintain a "Sliding Window" of the last 10 turns of raw dialogue (High Fidelity).
- **Periodic Summarizer**:
    - Once the raw history exceeds the window, trigger a background LLM call.
    - Prompt: *"Summarize the following interaction into 3-5 key plot points that must be remembered for future consistency."*
- **The "Narrative Seed"**:
    - The summary is appended to a persistent "Story So Far" block at the top of every prompt.
    - This seed replaces the raw text of the old turns, freeing up thousands of tokens for new generation.
- **Consistency Check**: Before committing a summary, the Director Agent validates that no crucial lore or character facts were lost during compression.

## Strategic Value
Allows for "infinite" story length. The engine will never "forget" the beginning of the adventure, even as it moves into Chapter 20.
