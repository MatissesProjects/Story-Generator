# Context Management Plan

## Objective
Build the Context Curator and integrate it into the generation loop.

## Implementation Steps
1.  **Keyword Extraction**: Implement a simple keyword extractor (or an LLM-based summarizer/entity extractor) on the latest user input.
2.  **Database Querying**: Extend `db.py` to support searching for lore and characters based on extracted keywords.
3.  **Prompt Assembly**: Modify `main.py` to gather this context and prepend it to the LLM prompt (e.g., `[SYSTEM: Consider these facts: ...]`).
4.  **Refinement**: Tune the amount of context included to prevent overwhelming the prompt.

## Verification
- Verify that mentioning a character's name pulls their sheet from the database and injects it into the prompt.
- Check that the LLM utilizes the injected context correctly in its output.