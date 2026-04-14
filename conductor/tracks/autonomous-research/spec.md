# Autonomous Research Specification

## Objective
Enable the story engine to perform autonomous online research to find "crazy new ideas," unique narrative hooks, and niche lore to prevent stories from becoming repetitive or predictable.

## Requirements
- **Search Integration**: A module (`researcher.py`) that can perform web searches based on current story themes or a "need for novelty."
- **Idea Extraction**: An LLM prompt that takes raw search results and extracts 2-3 "Unexpected Narrative Hooks."
- **Director Trigger**: The Director Agent should have a "Novelty Meter." If the story feels too conventional or has stalled, it triggers the Researcher.
- **Lore Injection**: Extracted ideas should be automatically added to the `Lore` table (marked as "External Inspiration") and the `Plot_Threads` table to be woven into the story.

## Strategic Value
Breaks the "LLM Echo Chamber." By pulling in real-world niche facts, weird science, or obscure mythology, the engine ensures that every story has a unique, "hand-crafted" feel.
