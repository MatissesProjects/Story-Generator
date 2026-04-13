# Development Workflow

## Principles
- **MVP First**: Build the core text loop and memory state before adding complex audio or network features.
- **Modular Design**: Ensure the LLM connection, memory retrieval, and TTS generation are separate modules to allow easy swapping (e.g., changing TTS engines later).
- **Test Locally**: Develop and test the generator on a single machine before splitting roles across the network.

## Track Progression
1.  **Core Engine & Memory**: Establish the foundation (Ollama + SQLite).
2.  **Spark Generator**: Build a tool to jump-start narratives when there's no initial idea.
3.  **Context Management**: Implement dynamic prompt injection to save context size.
4.  **Audio Polish**: Add Piper TTS for character voices.
5.  **Network Architecture**: Finalize the WebSocket server and client for the multi-PC setup.