# Roadmap v2: Advanced Narrative Intelligence

This roadmap outlines the next evolution of the Story-Generator, transitioning from a robust reactive system to a proactive, state-aware "Narrative Engine."

## Core Concepts
Based on industry standards for interactive narrative systems, the next generation of our engine will focus on **proactive coherence** and **emotional resonance**.

### 1. Adaptive Plot Planning (HTN)
Instead of linear milestones, we will move toward a **Hierarchical Task Network (HTN)** structure. This allows the Director to decompose high-level narrative goals (e.g., "The Hero discovers the truth") into dynamic sub-tasks that adapt to player subversion.

### 2. Emotional State Machines (OCC Model)
We will implement the **Ortony, Clore, and Collins (OCC)** emotional model. NPCs will no longer just have "Trust/Fear" meters, but will experience complex affective states (e.g., *Resentment* if the player achieves a goal that blocks the NPC's goal) which will directly color their LLM-generated dialogue.

### 3. Real-Time Drama Management (Tension Curve)
Implementation of a "Drama Manager" that explicitly monitors the **Narrative Tension Curve**. It will balance high-tension "Action Beats" with reflective "Meaning Beats" to prevent player fatigue and manage engagement.

### 4. Multimodal Sync (Atmospheric Layer)
Tightly coupling the `AtmosphereEngine` with the Drama Manager. Lighting (TINT), Music intensity, and Sound effects will respond dynamically to the tension level of the scene.

## New Tracks
- [ ] **`htn-planning`**: Implement a hierarchical planner for adaptive story arcs.
- [ ] **`emotional-modeling`**: Implement the OCC framework for character interiority.
- [ ] **`drama-management`**: Build the Tension Curve monitor and real-time pacing controller.
- [ ] **`multimodal-coupling`**: Synchronize visual/audio cues with narrative state.
