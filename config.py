import os

# Mode: 'LOCAL' (single PC) or 'NETWORK' (two PCs)
MODE = os.getenv("STORY_GEN_MODE", "LOCAL")

# Generator PC settings (used in NETWORK mode)
GENERATOR_HOST = os.getenv("STORY_GEN_HOST", "0.0.0.0")
GENERATOR_PORT = int(os.getenv("STORY_GEN_PORT", 8000))

# Ollama settings
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e4b")

# TTS settings
PIPER_EXE = os.getenv("PIPER_EXE", "piper")
MODELS_DIR = os.getenv("MODELS_DIR", "models")
AUDIO_OUTPUT_DIR = os.getenv("AUDIO_OUTPUT_DIR", "audio_output")

def get_websocket_url(host="localhost"):
    return f"ws://{host}:{GENERATOR_PORT}/ws"