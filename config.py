from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os

class Settings(BaseSettings):
    # Mode: 'LOCAL' (single PC) or 'NETWORK' (two PCs)
    MODE: str = Field(default="LOCAL", validation_alias="STORY_GEN_MODE")

    # Generator PC settings
    GENERATOR_HOST: str = Field(default="0.0.0.0", validation_alias="STORY_GEN_HOST")
    GENERATOR_PORT: int = Field(default=8000, validation_alias="STORY_GEN_PORT")

    # Ollama settings
    OLLAMA_URL: str = Field(default="http://localhost:11434/api/generate", validation_alias="OLLAMA_URL")
    OLLAMA_MODEL: str = Field(default="gemma4:26b", validation_alias="OLLAMA_MODEL") # Main creative model
    CREATIVE_MODEL: str = Field(default="gemma4:26b", validation_alias="CREATIVE_MODEL")
    FAST_MODEL: str = Field(default="gemma4:26b", validation_alias="FAST_MODEL") # Small model for logic/parsing
    OLLAMA_KEEP_ALIVE: str = Field(default="5m", validation_alias="OLLAMA_KEEP_ALIVE") # How long to keep model in VRAM
    OLLAMA_TIMEOUT: float = Field(default=600.0, validation_alias="OLLAMA_TIMEOUT")

    # Distributed settings
    GPU_NAME: str = Field(default="RTX 4090", validation_alias="GPU_NAME")
    OFFLOAD_VISION: bool = Field(default=False, validation_alias="OFFLOAD_VISION")

    # TTS settings
    PIPER_EXE: str = Field(default="piper", validation_alias="PIPER_EXE")
    MODELS_DIR: str = Field(default="voices", validation_alias="MODELS_DIR")
    AUDIO_OUTPUT_DIR: str = Field(default="audio_output", validation_alias="AUDIO_OUTPUT_DIR")
    
    # Unified Voice Registry
    DEFAULT_VOICE: str = "en_US-lessac-medium.onnx"
    NARRATOR_VOICE: str = "en_US-ryan-high.onnx"
    VOICE_PROFILES: dict = {
        "Deep Male": "en_US-ryan-high.onnx",
        "Melodic Female": "en_US-lessac-high.onnx",
        "Natural Female": "en_US-lessac-medium.onnx",
        "Upbeat Male": "en_US-joe-medium.onnx",
        "Energetic Female": "en_US-amy-medium.onnx",
        "British Male": "en_GB-alan-medium.onnx",
        "British Female": "en_GB-jenny_dioco-medium.onnx",
        "Scottish Female": "en_GB-alba-medium.onnx"
    }

    # Vector DB settings
    VECTOR_DB_PATH: str = Field(default="vector_db", validation_alias="VECTOR_DB_PATH")
    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2", validation_alias="EMBEDDING_MODEL")

    # Vision settings
    VISION_MODEL: str = Field(default="stabilityai/sdxl-turbo", validation_alias="VISION_MODEL")
    PORTRAITS_DIR: str = Field(default="static/portraits", validation_alias="PORTRAITS_DIR")
    ENVIRONMENTS_DIR: str = Field(default="static/environments", validation_alias="ENVIRONMENTS_DIR")
    MAP_TILES_DIR: str = Field(default="static/map_tiles", validation_alias="MAP_TILES_DIR")
    IMAGE_CACHE_ENABLED: bool = Field(default=True, validation_alias="IMAGE_CACHE_ENABLED")

    # Music settings
    AUDIO_SEQUENCER_PATH: str = Field(default="/home/matisse/GitHub/AudioSequencer", validation_alias="AUDIO_SEQUENCER_PATH")
    MUSIC_DB_PATH: str = Field(default="/home/matisse/GitHub/AudioSequencer/audio_library.db", validation_alias="MUSIC_DB_PATH")
    MUSIC_ENABLED: bool = Field(default=True, validation_alias="MUSIC_ENABLED")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-disable music if path doesn't exist
        if not os.path.exists(self.AUDIO_SEQUENCER_PATH):
            self.MUSIC_ENABLED = False

    def get_websocket_url(self, host: str = "localhost") -> str:
        return f"ws://{host}:{self.GENERATOR_PORT}/ws"

# Global settings instance
_settings = Settings()

def get_settings():
    return _settings

# For backward compatibility
MODE = _settings.MODE
GENERATOR_HOST = _settings.GENERATOR_HOST
GENERATOR_PORT = _settings.GENERATOR_PORT
OLLAMA_URL = _settings.OLLAMA_URL
OLLAMA_MODEL = _settings.OLLAMA_MODEL
CREATIVE_MODEL = _settings.CREATIVE_MODEL
FAST_MODEL = _settings.FAST_MODEL
OLLAMA_KEEP_ALIVE = _settings.OLLAMA_KEEP_ALIVE
OLLAMA_TIMEOUT = _settings.OLLAMA_TIMEOUT
GPU_NAME = _settings.GPU_NAME
OFFLOAD_VISION = _settings.OFFLOAD_VISION
PIPER_EXE = _settings.PIPER_EXE
MODELS_DIR = _settings.MODELS_DIR
AUDIO_OUTPUT_DIR = _settings.AUDIO_OUTPUT_DIR
DEFAULT_VOICE = _settings.DEFAULT_VOICE
NARRATOR_VOICE = _settings.NARRATOR_VOICE
VOICE_PROFILES = _settings.VOICE_PROFILES
VECTOR_DB_PATH = _settings.VECTOR_DB_PATH
EMBEDDING_MODEL = _settings.EMBEDDING_MODEL
VISION_MODEL = _settings.VISION_MODEL
PORTRAITS_DIR = _settings.PORTRAITS_DIR
ENVIRONMENTS_DIR = _settings.ENVIRONMENTS_DIR
MAP_TILES_DIR = _settings.MAP_TILES_DIR
IMAGE_CACHE_ENABLED = _settings.IMAGE_CACHE_ENABLED
AUDIO_SEQUENCER_PATH = _settings.AUDIO_SEQUENCER_PATH
MUSIC_DB_PATH = _settings.MUSIC_DB_PATH
MUSIC_ENABLED = _settings.MUSIC_ENABLED

def get_websocket_url(host="localhost"):
    return _settings.get_websocket_url(host)
