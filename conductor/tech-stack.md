# Tech Stack

## Core Backend (Generator PC)
- **Language**: Python 3.10+
- **LLM Engine**: Ollama (local API)
- **Database**: SQLite (for persistent memory, characters, lore)
- **Framework**: FastAPI (for WebSocket server and REST endpoints)

## Audio Processing
- **TTS Engine**: Piper TTS (local, fast generation)
- **Audio Routing**: PyAudio or similar for managing output if needed on the generator side, or serving files over HTTP.

## Client (Player PC)
- **Protocol**: WebSockets (for real-time text streaming and event triggers)
- **UI**: TBD (e.g., simple web interface via HTML/JS, or a local Python GUI like PyQt/Tkinter)

## Context & RAG
- **Retrieval**: Custom Python logic querying SQLite based on keyword/semantic matching against recent dialogue/action.