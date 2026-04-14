# DiceMaster Module Specification

## Objective
Introduce mechanical risk and formalized conflict resolution via a dice roll and Difficulty Class (DC) system, giving the player real agency and consequence.

## Requirements
- **Mechanical Trigger**: A specific intent (e.g., `> ATTEMPT Stealth`) that triggers a dice roll.
- **DC Resolver**: A module that uses the LLM to set a Difficulty Class based on world state (e.g., "The guards are alert, DC is 15").
- **Roll Logic**: Performs a digital roll (e.g., 1d20) and compares it to the DC.
- **Consequence Branching**:
    - **Success**: The LLM is prompted to narrate a positive outcome.
    - **Failure**: The LLM is prompted to narrate a complication or failure.
- **Visual Feedback**: Show the dice roll animation and "Success/Failure" result in the Web UI.

## Strategic Value
Solves the "AI Agreement" problem where the LLM always lets the player succeed. It adds tension, unpredictability, and a "game" feel to the narrative.
