# Character Relationship Graph Specification

## Objective
Implement a dynamic social layer that tracks weighted relationships between characters, influencing their dialogue and behavioral consistency.

## Requirements
- **Relationship Database**: A `Relationships` table tracking `char_a_id, char_b_id, trust_score, fear_score, affection_score`.
- **Interaction Log**: Track social events (e.g., "shared a meal," "saved from goblin") that influence scores.
- **Persona Context**: When a character is mentioned, their relationship with the player or other present characters is injected into the Persona Block.
- **Social Graph UI**: A visual representation (nodes and edges) of character connections in the frontend.

## Strategic Value
Ensures NPCs don't just react to the immediate turn but maintain "Emotional Memory." It forces the LLM to respect past interactions, making betrayals or bonds feel earned.
