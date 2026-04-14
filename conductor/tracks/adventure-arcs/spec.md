# Adventure Arcs Specification

## Objective
Allow for pre-defined story structures and milestones, transforming the continuous generation into structured "Chapters" or "Campaigns."

## Requirements
- **Arc Templates**: Support for JSON files defining an arc (e.g., `the_stolen_heirloom.json`).
- **Milestone Tracking**:
    - **Setup**: Initial hook and character intro.
    - **Inciting Incident**: The event that starts the quest.
    - **Rising Action**: Escalating stakes.
    - **Resolution**: Final payoff.
- **State Transitioning**: The Director Agent tracks when a milestone has been reached and switches the "Global State" to the next chapter.
- **Arc Library**: A folder of pre-written templates that can be "Loaded" into a new session.

## Strategic Value
Provides a framework for long-form writing. It ensures the story follows a satisfying dramatic curve rather than just being an infinite series of events.
