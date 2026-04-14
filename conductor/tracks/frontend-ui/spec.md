# Frontend UI Specification

## Objective
Create a modern, web-based interface to replace the CLI client. The UI should provide a rich interactive experience, showing the story text as it streams, playing character audio automatically, and offering tools to manage characters, lore, and plot points.

## Requirements
- **Web Interface**: A single-page application (SPA) built with Vanilla HTML/JS/CSS.
- **WebSocket Integration**: Connect to the same `ws://localhost:8000/ws` endpoint.
- **Streaming Text**: Real-time display of the LLM's narrative output.
- **Audio Playback**: Automatic queueing and playback of character speech files.
- **Dashboard Sidebar**: 
    - Display the current "Story So Far" (Narrative Seed).
    - List active "Plot Threads."
    - Show recent "Research Inspiration" findings.
- **Command Forms**: Easy-to-use inputs for:
    - Adding characters (name, traits, description).
    - Adding lore and meta-narrative topics.
    - Manually adding plot threads.
- **System Logs**: A dedicated "Debug/Info" console to see context facts being used and background processes (like summarization or research).

## Strategic Value
Makes the tool accessible and visually engaging. It allows the user to see the "brain" of the engine working in real-time while enjoying a polished, narrative-first reading experience.
