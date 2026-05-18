"""Configuration management for ARAXON."""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""
    APP_NAME: str = "ARAXON"
    DEBUG_MODE: bool = False
    LOG_LEVEL: str = "INFO"
    GROQ_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    WAKE_WORD: str = "araxon"
    CHROMA_DB_PATH: str = "./data/chromadb"
    MODEL_DIR: str = "./models"
    SAMPLE_RATE: int = 16000
    VAD_THRESHOLD: float = 0.5
    SILENCE_DURATION: float = 1.5
    MIN_SPEECH_DURATION: float = 0.5
    VOICE_CHUNK_DURATION: float = 0.032
    HF_TOKEN: Optional[str] = None
    WHISPER_MODEL_SIZE: str = "base"
    WHISPER_LANGUAGE: str = "en"
    TTS_VOICE: str = "af_heart"
    TTS_SPEED: float = 1.0
    TTS_SAMPLE_RATE: int = 24000
    TTS_CHUNK_SIZE: int = 150

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()