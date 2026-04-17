# 🎭 Local Story Generator: Cinematic Engine

A completely local, multi-PC story generation tool that transforms interactive fiction into a professional **Cinematic Experience**. It leverages a local LLM (Ollama) to generate proactive narratives, maintaining a living world with independent NPCs, dynamic weather, and multi-layered Visual Novel aesthetics.

## 🌟 Vision
The Local Story Generator isn't just a chatbot—it's a living world simulation. By splitting the heavy lifting (LLM generation/Vision) from the player interface, it delivers a rich, multisensory experience with character voices, environment art, and reactive visual effects across a local network.

## 🚀 Key Features

### 🎬 Cinematic Experience V2
- **Layered VN Staging**: Independent layers for Environment, 3 Character Slots (Left, Center, Right), and Overlays.
- **On-Demand Asset Pipeline**: Missing images are automatically generated on-the-fly by the **Vision Engine** (SDXL Turbo) and cached.
- **Reactive UI**: The dialogue box and name tags dynamically shift styles based on the detected mood (Tension, Combat, Mystical).
- **Camera Work**: Automated Ken Burns effects (pan/zoom) and screen shakes bring static art to life.

### 🌍 The Living World
- **Global Simulation Tick**: The world advances time independently. Background events (Political, Environmental) occur every few turns.
- **Proactive NPC Agency**: NPCs have internal motivations (Social, Ambition, Safety) and will move, work, or socialize autonomously.
- **Narrative Entropy**: Relationships decay over time toward "anchors," and lore can mutate into rumors, simulating the passage of time.
- **Lore Duels**: Automated resolution of canon contradictions using LLM-driven reconciliation.

### 🔊 Immersive Audio & VJ Visuals
- **Streaming Audio**: Dialogue is parsed and converted to TTS in real-time while the story streams.
- **Multimodal Atmosphere**: Synchronized lighting, weather, and looping background ambiance (wind, rain, tavern noise).
- **VJ Visuals**: Dynamic blending of textures and overlays (glitches, dust, scanlines) based on narrative tension.

## 🛠️ Tech Stack
- **LLM**: Ollama (default: `gemma4:e4b`)
- **Vision**: Stable Diffusion (SDXL Turbo) via `diffusers`
- **TTS**: Piper TTS
- **Database**: SQLite + ChromaDB (Vector)
- **Backend**: Python (FastAPI + WebSockets)
- **Frontend**: Vanilla JS / CSS3 (Layered Blending)

## 📋 Prerequisites
1. **Ollama**: Install and run Ollama. Pull your model (`ollama pull gemma4:e4b`).
2. **Piper TTS**: Download the Piper executable and `.onnx` models.
3. **GPU**: A modern GPU (e.g., RTX 4090) is recommended for real-time Vision/LLM generation.

## 📖 Usage

### 1. Network Mode (Recommended)
**Step A: Start the Generator Server**
```bash
python server.py
```
**Step B: Access the Web Interface**
Open `http://localhost:8000` in your browser. The engine will automatically orchestrate the visuals, audio, and narrative.

### 2. On-Demand Asset Generation
Simply add a character or move to a new location. If the image isn't in your `portraits` or `environments` folder, the server will call `/asset/{type}/{name}` and generate it for you instantly.

## 📂 Project Structure
- `agency_engine.py`: Proactive NPC motivation and Utility AI.
- `atmosphere_engine.py`: Environmental cues (lighting, weather, ambiance).
- `visual_curator.py`: Automated layer management and character staging.
- `simulation_manager.py`: Global time progression and background events.
- `entropy_engine.py`: Relationship decay and lore volatility.
- `canon_checker.py`: Lore duel resolution and factual audit.
- `vision.py`: Local SDXL Turbo image generation.
- `server.py`: FastAPI WebSocket orchestrator.

## 📜 License
[MIT License](LICENSE)
