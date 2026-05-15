# Product Definition: Story Generator

## Vision
A completely local, multi-PC story generation tool that co-writes interactive fiction. It transitions from a reactive generative system to an autonomous "Narrative Engine" capable of proactive coherence, complex emotional resonance, and real-time drama management.

## Key Features
- **Local Generation**: Uses Ollama for LLM inference, ensuring privacy and offline capability.
- **Persistent Memory**: SQLite database and ChromaDB vector store manage character sheets, world lore, and plot timelines.
- **Narrative Intelligence (v2)**: Advanced planning (HTN), emotional modeling (OCC), and drama management ensure proactive and coherent storytelling.
- **Multimodal Performance**: Tightly coupled character voices (Piper TTS), cinematic visuals, and atmospheric synchronization (lighting/music).
- **Multi-PC Architecture**: A WebSocket-based push architecture allows for high-performance task offloading (e.g., separating LLM, Vision, and Audio).