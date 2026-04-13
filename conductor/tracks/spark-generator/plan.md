# Spark Generator Plan

## Objective
Implement the Spark Generator to bootstrap narratives.

## Implementation Steps
1.  **Prompt Templates**: Define a set of system prompts designed purely for idea generation (e.g., "Generate a brief, compelling premise for a fantasy story involving a lost artifact and an unlikely hero.").
2.  **Generator Logic**: Create a `spark.py` module that selects a template, potentially fills in random parameters, and calls the `llm.py` interface.
3.  **Integration**: Allow the main application loop to offer a "Generate Spark" option at startup.

## Verification
- Test generating multiple diverse sparks.
- Verify a generated spark can successfully initialize a new story session and populate initial `Lore` or `Characters` in the database.