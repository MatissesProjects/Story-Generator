# Local Story Generator

A completely local, multi-PC story generation tool that co-writes interactive fiction. It leverages a local LLM (Ollama) to generate narratives, maintaining persistent world states and character voices using local TTS (Piper).

## 🌟 Vision
The Local Story Generator is designed for immersive, private, and customizable storytelling. By splitting the heavy lifting (LLM generation) from the player interface (text streaming and audio playback), it allows for a rich experience even on modest hardware configurations across a local network.

## 🚀 Key Features
- **Local Generation**: Powered by [Ollama](https://ollama.ai/) for full privacy and offline capability.
- **Persistent Memory**: A SQLite-backed memory system stores character sheets, world lore, and plot timelines, ensuring long-term narrative consistency.
- **Context Management (The Curator)**: Instead of sending the entire story history, the **Curator** dynamically filters and injects only the most relevant lore and character facts into the LLM prompt.
- **State Update Loop**: The system follows a continuous loop: User Input → Context Retrieval → LLM Generation → State Update & Audio Playback.
- **Character Voices**: Uses [Piper TTS](https://github.com/rhasspy/piper) to provide distinct, localized voices for characters during dialogue segments.
- **Multi-PC Architecture**: WebSocket-based architecture allows a dedicated **Generator PC** to handle LLM/TTS tasks while a **Player PC** handles the interface and audio playback.
- **Spark Generator**: Need a starting point? The Spark module generates creative story seeds and world prompts.

## 🛠️ Tech Stack
- **LLM**: Ollama (default model: `gemma4:e4b` or similar)
- **TTS**: Piper TTS
- **Database**: SQLite
- **Backend**: Python, FastAPI, Uvicorn
- **Communication**: WebSockets

## 📋 Prerequisites
1. **Ollama**: Install and run Ollama. Pull your preferred model (e.g., `ollama pull gemma4:e4b`).
2. **Piper TTS**: Download the Piper executable and relevant `.onnx` voice models.
3. **Python 3.10+**: Ensure Python is installed.

### Dependencies
Install the required Python packages:
```bash
pip install requests fastapi uvicorn websockets pydantic-settings pydantic
```

## ⚙️ Configuration
Configuration is managed via `config.py` and can be overridden using a `.env` file:
- `STORY_GEN_MODE`: `LOCAL` or `NETWORK`
- `OLLAMA_URL`: URL for the Ollama API
- `OLLAMA_MODEL`: The model name to use
- `PIPER_EXE`: Path to the Piper executable
- `MODELS_DIR`: Directory containing Piper voice models

## 📖 Usage

### 1. Local Mode (Single PC)
Run the generator in a single terminal for a direct CLI experience:
```bash
python main.py
```
**Interactive Commands:**
- `spark`: Generate a random story idea.
- `add character`: Create a new character with a specific voice.
- `add lore`: Add world-building facts to the persistent memory.
- `exit`: Quit the application.

### 2. Network Mode (Multi-PC)

#### **Step A: Start the Generator Server (Generator PC)**
```bash
python server.py
```

#### **Step B: Start the Player Client (Player PC)**
```bash
python client.py --host <GENERATOR_IP>
```
The client will connect to the server, stream story segments, and play character dialogue audio locally.

## 📂 Project Structure
- `main.py`: Entry point for local mode.
- `server.py`: FastAPI WebSocket server for network mode.
- `client.py`: WebSocket client for the player interface.
- `llm.py`: Ollama API integration.
- `tts.py`: Piper TTS integration and audio playback.
- `db.py` & `schema.sql`: Database management for world state.
- `curator.py`: Logic for retrieving relevant context for prompts.
- `spark.py`: Story seed generation logic.
- `parser.py`: Dialogue and action parsing for audio triggering.
- `config.py`: Global settings and environment handling.

## 📜 License
[MIT License](LICENSE) (or your preferred license)
