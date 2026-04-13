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
    OLLAMA_MODEL: str = Field(default="gemma4:e4b", validation_alias="OLLAMA_MODEL")

    # TTS settings
    PIPER_EXE: str = Field(default="piper", validation_alias="PIPER_EXE")
    MODELS_DIR: str = Field(default="models", validation_alias="MODELS_DIR")
    AUDIO_OUTPUT_DIR: str = Field(default="audio_output", validation_alias="AUDIO_OUTPUT_DIR")

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
PIPER_EXE = _settings.PIPER_EXE
MODELS_DIR = _settings.MODELS_DIR
AUDIO_OUTPUT_DIR = _settings.AUDIO_OUTPUT_DIR

def get_websocket_url(host="localhost"):
    return _settings.get_websocket_url(host)
