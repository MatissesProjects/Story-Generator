# Network Architecture Specification

## Objective
Transition the application from a single script to a multi-PC architecture using WebSockets, separating the heavy Generation work from the Player interface.

## Requirements
- A WebSocket server running on the "Generator PC" using FastAPI.
- A client application (or simple web UI) running on the "Player PC".
- Real-time streaming of text and synchronized triggering of audio playback across the network.