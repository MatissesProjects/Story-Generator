# Foreshadowing Engine Specification

## Objective
Track minor narrative details and "unresolved seeds" to ensure they receive meaningful payoffs later in the story, creating a sense of deliberate and professional pacing.

## Requirements
- **Seed Tracking**: A `Foreshadowed_Elements` table tracking `element_name, discovery_location, potential_impact, payoff_status`.
- **Lull Analysis**: The Director Agent identifies narrative "lulls" (slow pacing) and queries the foreshadowing table for a "call back" opportunity.
- **Organic Re-injection**: The system injects a hidden instruction: "Re-introduce the [Strange Silver Coin] mentioned in [The Marketplace] as a relevant clue for this scene."

## Strategic Value
Prevents the "Forgotten Plot Hole" syndrome common in free-form LLM generation. It makes the story feel like it was written by a human who knows the ending, even though it's generated turn-by-turn.
