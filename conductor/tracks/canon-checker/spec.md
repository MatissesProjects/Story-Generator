# Canon Checker Specification

## Objective
Implement an advanced lore validation layer that analyzes LLM-generated concepts against established "World Canon" to prevent contradictions and maintain deep consistency.

## Requirements
- **Post-Generation Analysis**: After the LLM generates a response, a fast, strictly-canonicity-focused model scans it for new world-building claims.
- **Canon Matching**: Claims are compared against the `Lore` and `Meta_Lore` tables.
- **Contradiction Flagging**: If a response claims "Dragons are immortal" but the lore says "Dragons die of old after 500 years," the system flags a "Canon Violation."
- **Self-Correction**: The system prompts the main LLM to re-write the offending segment to align with established canon.

## Strategic Value
Maintains the integrity of the world. As stories grow long, LLMs often hallucinate new rules; the Canon Checker ensures that "The rules are the rules" regardless of how many turns have passed.
