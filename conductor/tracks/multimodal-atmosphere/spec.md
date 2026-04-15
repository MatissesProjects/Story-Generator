# 🎭 Track: Multimodal Atmosphere

## Overview
Standardize and synchronize sensory feedback (visual atmosphere, weather, soundscapes) to create a more immersive narrative experience. This track bridge the gap between "text" and "experience" by providing structured signals for frontends to react to.

## Core Objectives
- **Atmosphere Codes**: A structured JSON format for environmental state (e.g., `{ "lighting": "dim_red", "weather": "thunderstorm", "haptic": "low_rumble" }`).
- **Dynamic Soundscapes**: Real-time selection of ambient background loops that layer with the existing music system.
- **Atmospheric Extraction**: Use the LLM to automatically detect when the story's environment changes and output the correct codes.
- **Frontend-Ready Hooks**: Ensure the WebSocket sends clear, actionable signals for UI effects (screen shakes, color tints, particle effects).

## Functional Requirements
1. **The Atmosphere Engine**: A new module `atmosphere_engine.py` to manage state and logic.
2. **Unified Atmosphere Message**: A new WebSocket message type `atmosphere_update`.
3. **Soundscape Library**: Integration with the `AudioSequencer` for non-music ambient loops (wind, rain, tavern noise).

## Dependencies
- `music_orchestrator.py`: For layering music with soundscapes.
- `server.py`: For delivering real-time atmospheric signals.
- `llm.py`: For extracting environmental cues from text.
