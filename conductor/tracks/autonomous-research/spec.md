# Autonomous Research Specification

## Objective
Enable the story engine to perform autonomous online research to find "crazy new ideas," unique narrative hooks, and niche lore to prevent stories from becoming repetitive or predictable.

## Requirements
- **Search Integration**: A module (`researcher.py`) that can perform web searches based on current story themes or a "need for novelty."
- **Narrative Gap Analysis**: The Director Agent analyzes the recent history and active plot threads to identify "stalled" or "repetitive" themes. It then generates a "Research Mission" to inject new energy.
- **Search Query Optimization**: An LLM-powered pre-processor that turns broad themes into high-signal search queries (e.g., "weirdest biological survival strategies in extreme environments").
- **Idea Extraction**: An LLM prompt that takes raw search results and extracts 2-3 "Unexpected Narrative Hooks."
- **Lore & Entity Injection**: Extracted ideas are automatically added to the `Lore` table and can optionally spawn new `Characters` or `Items` to give the research a physical presence in the world.

## Strategic Value
Breaks the "LLM Echo Chamber." By pulling in real-world niche facts, weird science, or obscure mythology, the engine ensures that every story has a unique, "hand-crafted" feel and prevents the AI from falling into repetitive tropes.
