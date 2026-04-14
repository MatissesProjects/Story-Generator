# DiceMaster Module Specification

## Objective
Introduce mechanical risk and formalized conflict resolution via a dice roll and Difficulty Class (DC) system, giving the player real agency and consequence.

## Requirements
- **Hidden Conflict Resolution**: The system automatically identifies risky actions and performs a hidden dice roll.
- **Selective Visibility**: The result of the roll is only shown to the user (e.g., "Roll: 14 vs DC 12 - Success!") if it adds significant dramatic weight or if the player explicitly asks for a check.
- **DC Resolver**: The Director Agent automatically sets a Difficulty Class (DC) based on the current context and active "Active Leads."
- **Interpretive Narration**:
    - The roll result is injected into the LLM prompt: `[MECHANICAL RESULT: SUCCESS (Roll 18 vs DC 15). Describe a narrow but impressive victory.]`
    - The LLM's primary job is to narrate the *consequence* of the mechanics, ensuring the player feels the impact of the RNG without always seeing the "math."
- **Status Metadata**: The UI can optionally show a small "Outcome Indicator" (e.g., a green or red spark) to hint at the roll result without full text.

## Strategic Value
Solves the "AI Agreement" problem where the LLM always lets the player succeed. It adds tension, unpredictability, and a "game" feel to the narrative.
