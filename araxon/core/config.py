"""Configuration management for ARAXON."""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""
    APP_NAME: str = "ARAXON"
    DEBUG_MODE: bool = False
    LOG_LEVEL: str = "INFO"
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama3-8b-8192"
    OLLAMA_MODEL: str = "llama3"
    PREFERRED_BACKEND: str = "groq"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    MAX_MEMORY_TURNS: int = 20
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 300
    WAKE_WORD: str = "araxon"
    WAKE_PHRASES: list[str] = ["hey araxon", "araxon", "ok araxon", "wake up araxon"]
    SLEEP_PHRASES: list[str] = ["go to sleep", "standby", "sleep mode", "goodbye araxon"]
    RESET_PHRASES: list[str] = ["reset memory", "forget everything", "clear memory"]
    WAKE_WORD_ENABLED: bool = True
    WAKE_CONFIRMATION_PHRASE: str = "I'm listening."
    WAKE_SLEEP_PHRASE: str = "Going to standby. Double clap or say my name to wake me."
    STANDBY_MODE_ENABLED: bool = True
    AUTO_SLEEP_TIMEOUT_SECONDS: int = 300
    AUTO_SLEEP_CHECK_INTERVAL_SECONDS: int = 30
    CLAP_ENERGY_THRESHOLD: float = 0.3
    CLAP_MIN_GAP_MS: int = 100
    CLAP_MAX_GAP_MS: int = 800
    CLAP_SUPPRESSION_WINDOW_MS: int = 2000
    CLAP_FRAME_DURATION_SECONDS: float = 0.03
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHROMA_DB_PATH: str = "./data/chromadb"
    CHROMA_COLLECTION_CONVERSATIONS: str = "araxon_conversations"
    CHROMA_COLLECTION_FILES: str = "araxon_files"
    RAG_ENABLED: bool = True
    RAG_MAX_RESULTS: int = 4
    RAG_SIMILARITY_THRESHOLD: float = 0.6
    RAG_INJECT_INTO_SYSTEM: bool = True
    INGESTION_FOLDER: str = "./data/ingested"
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
    APP_MAP: dict[str, str] = {
        "vs code": "code",
        "vscode": "code",
        "terminal": "cmd",
        "spotify": "spotify",
        "chrome": "chrome",
        "firefox": "firefox",
        "explorer": "explorer",
        "notepad": "notepad",
        "discord": "discord",
        "slack": "slack",
    }
    WEBSITE_MAP: dict[str, str] = {
        "youtube": "https://youtube.com",
        "github": "https://github.com",
        "google": "https://google.com",
        "stackoverflow": "https://stackoverflow.com",
        "gmail": "https://mail.google.com",
        "reddit": "https://reddit.com",
        "twitter": "https://twitter.com",
        "linkedin": "https://linkedin.com",
        "chatgpt": "https://chat.openai.com",
        "localhost": "http://localhost:3000",
    }
    BROWSER_HEADLESS: bool = False
    BROWSER_TIMEOUT_MS: int = 10000
    COMMAND_TIMEOUT_SECONDS: int = 30
    ALLOWED_COMMANDS: list[str] = ["npm", "python", "pip", "git", "node", "uvicorn", "pytest", "ls", "dir"]
    COMMAND_MAP: dict[str, str] = {
        "run server": "npm run dev",
        "start server": "npm run dev",
        "run python": "python main.py",
        "install packages": "pip install -r requirements.txt",
        "git status": "git status",
        "git push": "git push",
        "run tests": "pytest",
    }
    WORKSPACE_PROFILES: dict[str, list[str]] = {
        "mern": [
            "code .",
            "start cmd /k npm run dev",
            "http://localhost:3000",
        ],
        "python": [
            "code .",
            "start cmd /k python main.py",
        ],
        "ai": [
            "code .",
            "start cmd /k ollama serve",
            "http://localhost:11434",
        ],
        "focus": [
            "spotify",
            "code .",
        ],
    }

    # Agent settings (STEP 8)
    AGENT_MAX_STEPS: int = 10
    AGENT_PLANNING_ENABLED: bool = True
    AGENT_NARRATE_STEPS: bool = True
    AGENT_STEP_DELAY_SECONDS: float = 1.0
    AGENT_MAX_ITERATIONS: int = 15
    AGENT_USE_REACT: bool = True
    AGENT_MODE: str = "graph"

    # Internet Intelligence settings (STEP 9)
    SEARCH_MAX_RESULTS: int = 5
    SEARCH_REGION: str = "wt-wt"
    SEARCH_SAFE_MODE: bool = True
    EXTRACTOR_MAX_CHARS: int = 2000
    EXTRACTOR_TIMEOUT_SECONDS: int = 10
    RESEARCH_MAX_SOURCES: int = 3
    RESEARCH_SAVE_TO_MEMORY: bool = True
    NEWS_MAX_ARTICLES: int = 5
    NEWS_DEFAULT_TOPIC: str = "technology"
    WIKI_LANGUAGE: str = "en"
    WIKI_MAX_CHARS: int = 500
    WIKI_USER_AGENT: str = 'ARAXON/1.0 (https://github.com/lucky/araxon; lucky@example.com)'

    # Vision System settings (STEP 10)
    SCREENSHOT_SAVE_PATH: str = "./logs/screenshots"
    SCREENSHOT_FORMAT: str = "png"
    SCREENSHOT_QUALITY: int = 95
    VISION_MONITOR_INDEX: int = 1
    TESSERACT_PATH: str = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    OCR_LANGUAGE: str = "eng"
    OCR_MIN_CONFIDENCE: int = 60
    VISION_ANALYSIS_ENABLED: bool = True
    VISION_MAX_TEXT_CHARS: int = 1500

    # UI System settings (STEP 11)
    UI_ENABLED: bool = True
    UI_WEBSOCKET_HOST: str = "localhost"
    UI_WEBSOCKET_PORT: int = 8765
    UI_MAX_TRANSCRIPT_ENTRIES: int = 100
    UI_SYSTEM_STATS_UPDATE_INTERVAL: float = 5.0
    UI_WAVEFORM_UPDATE_INTERVAL: float = 0.1

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()
