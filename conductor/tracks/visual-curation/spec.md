# 📺 Track: VJ Visual Curation

## Overview
Implement a dynamic visual curation system that manages multiple layers of imagery (Backgrounds, Characters, Overlays, and Textures) to create a VJ-like experience. The system should automatically curate and transition between visuals based on narrative mood and atmospheric codes.

## Core Objectives
- **Layered Visual Stack**: Move from a single background image to a multi-layer setup (Base, Environment, Entity, Atmosphere).
- **Automated Curator**: A module `visual_curator.py` that selects the best assets from the generated library and external textures.
- **Dynamic Transitions**: Implement smooth fades, glitches, and blending modes on the frontend.
- **Visual Feedback Loop**: Visuals should react to "Atmosphere Codes" (e.g., flickering during a storm, glitching during a magical anomaly).

## Functional Requirements
1. **The Visual Stack**:
   - `Layer 0: Texture/Base`: Ambient movement or static color.
   - `Layer 1: Environment`: The location artwork.
   - `Layer 2: Entity`: Portraits of characters in the scene.
   - `Layer 3: Overlay`: Weather effects, particles, or screen tints.
2. **The Visual Curator**:
   - Scans `db.py` for relevant characters/locations.
   - Decides which "Mood Textures" to apply.
   - Sends a unified `visual_update` message.

## Dependencies
- `vision.py`: For generating new assets as needed.
- `atmosphere_engine.py`: For driving the visual effects (shaking, tinting).
- `server.py`: For orchestrating the visual message.
