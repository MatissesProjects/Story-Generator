# Quest System Specification

## Objective
Implement a structured quest and objective tracking system to give the narrative clear direction, purpose, and measurable progress.

## Requirements
- **Structured Goals**: A `Quests` table in SQLite tracking `id, title, description, reward, status (Active, Completed, Failed)`.
- **Granular Objectives**: A `Quest_Objectives` table for multi-step tasks within a quest.
- **Narrative Prioritization**: The `curator.py` module will prioritize active quest objectives when building the LLM context.
- **Quest Log UI**: A dedicated section in the frontend sidebar to display active quests and their progress.
- **Autonomous Quest Generation**: The Director Agent can propose new quests based on story events or "Autonomous Research" findings.

## Strategic Value
Quests transform the story from a passive experience into an active journey. They provide the "Why" behind character actions and ensure the LLM stays focused on long-term resolutions.
