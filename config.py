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

    # TTS settings
    PIPER_EXE: str = Field(default="piper", validation_alias="PIPER_EXE")
    MODELS_DIR: str = Field(default="models", validation_alias="MODELS_DIR")
    AUDIO_OUTPUT_DIR: str = Field(default="audio_output", validation_alias="AUDIO_OUTPUT_DIR")

    # Vector DB settings
    VECTOR_DB_PATH: str = Field(default="vector_db", validation_alias="VECTOR_DB_PATH")
    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2", validation_alias="EMBEDDING_MODEL")

    # Vision settings
    VISION_MODEL: str = Field(default="stabilityai/sdxl-turbo", validation_alias="VISION_MODEL")
    PORTRAITS_DIR: str = Field(default="static/portraits", validation_alias="PORTRAITS_DIR")
    ENVIRONMENTS_DIR: str = Field(default="static/environments", validation_alias="ENVIRONMENTS_DIR")
    MAP_TILES_DIR: str = Field(default="static/map_tiles", validation_alias="MAP_TILES_DIR")

    # Music settings
    AUDIO_SEQUENCER_PATH: str = Field(default="/home/matisse/GitHub/AudioSequencer", validation_alias="AUDIO_SEQUENCER_PATH")
    MUSIC_DB_PATH: str = Field(default="/home/matisse/GitHub/AudioSequencer/audio_library.db", validation_alias="MUSIC_DB_PATH")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

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
PIPER_EXE = _settings.PIPER_EXE
MODELS_DIR = _settings.MODELS_DIR
AUDIO_OUTPUT_DIR = _settings.AUDIO_OUTPUT_DIR
VECTOR_DB_PATH = _settings.VECTOR_DB_PATH
EMBEDDING_MODEL = _settings.EMBEDDING_MODEL
VISION_MODEL = _settings.VISION_MODEL
PORTRAITS_DIR = _settings.PORTRAITS_DIR
ENVIRONMENTS_DIR = _settings.ENVIRONMENTS_DIR
MAP_TILES_DIR = _settings.MAP_TILES_DIR
AUDIO_SEQUENCER_PATH = _settings.AUDIO_SEQUENCER_PATH
MUSIC_DB_PATH = _settings.MUSIC_DB_PATH

def get_websocket_url(host="localhost"):
    return _settings.get_websocket_url(host)
