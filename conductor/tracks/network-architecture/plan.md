# Network Architecture Plan

## Objective
Build the WebSocket server and client infrastructure.

## Implementation Steps
1.  **FastAPI Server**: Refactor the main loop into a FastAPI application (`server.py`) with a WebSocket endpoint.
2.  **Streaming Logic**: Modify the LLM and TTS pipelines to emit events (e.g., `{"type": "text", "content": "..."}`, `{"type": "audio_ready", "url": "..."}`) over the WebSocket connection.
3.  **Client Application**: Build a lightweight client (`client.py` or HTML/JS) that connects to the server, displays incoming text, and fetches/plays audio when instructed.
4.  **Network Testing**: Test the connection across two separate PCs on the local network.

## Verification
- Verify successful WebSocket connection from the Player PC to the Generator PC.
- Ensure text streams smoothly on the Player PC.
- Confirm audio plays on the Player PC synchronized with the text.