"""Configuration management for ARAXON."""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""
    APP_NAME: str = "ARAXON"
    DEBUG_MODE: bool = False
    LOG_LEVEL: str = "INFO"
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.1-8b-instant"
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
    VAD_THRESHOLD: float = 0.3
    SILENCE_DURATION: float = 1.8
    MIN_SPEECH_DURATION: float = 0.3
    VOICE_CHUNK_DURATION: float = 0.032
    HF_TOKEN: Optional[str] = None
    WHISPER_MODEL_SIZE: str = "small"
    WHISPER_LANGUAGE: str = "en"
    TTS_VOICE: str = "af_heart"
    TTS_SPEED: float = 1.0
    TTS_SAMPLE_RATE: int = 24000
    TTS_CHUNK_SIZE: int = 150
    APP_MAP: dict[str, str] = {
        "vs code": "Microsoft.VisualStudioCode",
        "vscode": "Microsoft.VisualStudioCode",
        "visual studio code": "Microsoft.VisualStudioCode",
        "code": "Microsoft.VisualStudioCode",
        "cursor": "Anysphere.Cursor",
        "spotify": "SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify",
        "chrome": "Chrome",
        "google chrome": "Chrome",
        "firefox": "firefox",
        "edge": "MSEdge",
        "microsoft edge": "MSEdge",
        "terminal": "Microsoft.WindowsTerminal_8wekyb3d8bbwe!App",
        "windows terminal": "Microsoft.WindowsTerminal_8wekyb3d8bbwe!App",
        "notepad": "Microsoft.WindowsNotepad_8wekyb3d8bbwe!App",
        "calculator": "Microsoft.WindowsCalculator_8wekyb3d8bbwe!App",
        "paint": "Microsoft.Paint_8wekyb3d8bbwe!App",
        "discord": "com.squirrel.Discord.Discord",
        "telegram": "TelegramMessengerLLP.TelegramDesktop_t4vj0pshhgkwm!Telegram.TelegramDesktop",
        "whatsapp": "5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
        "instagram": "Facebook.InstagramBeta_8xx8rvfyw5nnt!App",
        "outlook": "Microsoft.OutlookForWindows_8wekyb3d8bbwe!Microsoft.OutlookforWindows",
        "teams": "MSTeams_8wekyb3d8bbwe!MSTeams",
        "microsoft teams": "MSTeams_8wekyb3d8bbwe!MSTeams",
        "word": "Microsoft.Office.WINWORD.EXE.15",
        "excel": "Microsoft.Office.EXCEL.EXE.15",
        "powerpoint": "Microsoft.Office.POWERPNT.EXE.15",
        "onenote": "Microsoft.Office.ONENOTE.EXE.15",
        "access": "Microsoft.Office.MSACCESS.EXE.15",
        "todo": "Microsoft.Todos_8wekyb3d8bbwe!App",
        "to do": "Microsoft.Todos_8wekyb3d8bbwe!App",
        "sticky notes": "Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe!App",
        "photos": "Microsoft.Windows.Photos_8wekyb3d8bbwe!App",
        "camera": "Microsoft.WindowsCamera_8wekyb3d8bbwe!App",
        "clock": "Microsoft.WindowsAlarms_8wekyb3d8bbwe!App",
        "weather": "Microsoft.BingWeather_8wekyb3d8bbwe!App",
        "news": "Microsoft.BingNews_8wekyb3d8bbwe!AppexNews",
        "maps": "Microsoft.WindowsMaps_8wekyb3d8bbwe!App",
        "store": "Microsoft.WindowsStore_8wekyb3d8bbwe!App",
        "microsoft store": "Microsoft.WindowsStore_8wekyb3d8bbwe!App",
        "xbox": "Microsoft.GamingApp_8wekyb3d8bbwe!Microsoft.Xbox.App",
        "game bar": "Microsoft.XboxGamingOverlay_8wekyb3d8bbwe!App",
        "snipping tool": "Microsoft.ScreenSketch_8wekyb3d8bbwe!App",
        "snip": "Microsoft.ScreenSketch_8wekyb3d8bbwe!App",
        "media player": "Microsoft.ZuneMusic_8wekyb3d8bbwe!Microsoft.ZuneMusic",
        "films": "Microsoft.ZuneVideo_8wekyb3d8bbwe!Microsoft.ZuneVideo",
        "tv": "Microsoft.ZuneVideo_8wekyb3d8bbwe!Microsoft.ZuneVideo",
        "vlc": "{6D809377-6AF0-444B-8957-A3773F02200E}\\VideoLAN\\VLC\\vlc.exe",
        "postman": "com.squirrel.Postman.Postman",
        "github desktop": "com.squirrel.GitHubDesktop.GitHubDesktop",
        "mongodb compass": "com.squirrel.MongoDBCompass.MongoDBCompass",
        "mongodb": "com.squirrel.MongoDBCompass.MongoDBCompass",
        "bluestacks": "BlueStacks_nxt",
        "epic games": "{6D809377-6AF0-444B-8957-A3773F02200E}\\Epic Games\\Launcher\\Portal\\Binaries\\Win32\\EpicGamesLauncher.exe",
        "premiere": "{6D809377-6AF0-444B-8957-A3773F02200E}\\Adobe\\Adobe Premiere Pro 2025\\Adobe Premiere Pro.exe",
        "adobe premiere": "{6D809377-6AF0-444B-8957-A3773F02200E}\\Adobe\\Adobe Premiere Pro 2025\\Adobe Premiere Pro.exe",
        "ollama": "C:\\Users\\lucky\\AppData\\Local\\Programs\\Ollama\\ollama app.exe",
        "task manager": "Microsoft.AutoGenerated.{923DD477-5846-686B-A659-0FCCD73851A8}",
        "control panel": "Microsoft.Windows.ControlPanel",
        "settings": "windows.immersivecontrolpanel_cw5n1h2txyewy!microsoft.windows.immersivecontrolpanel",
        "file explorer": "Microsoft.Windows.Explorer",
        "explorer": "Microsoft.Windows.Explorer",
        "copilot": "Microsoft.Copilot_8wekyb3d8bbwe!App",
        "power automate": "Microsoft.PowerAutomateDesktop_8wekyb3d8bbwe!PAD.Console",
        "zoom": "zoom.us.Zoom Video Meetings",
        "warp": "dev.warp.Warp",
        "canva": "com.canva.CanvaDesktop",
        "sql server": "SSMS.7cca30d5",
        "ssms": "SSMS.7cca30d5",
        "mysql workbench": "{6D809377-6AF0-444B-8957-A3773F02200E}\\MySQL\\MySQL Workbench 8.0 CE\\MySQLWorkbench.exe",
        "nvidia": "NVIDIACorp.NVIDIAControlPanel_56jybvy8sckqj!NVIDIACorp.NVIDIAControlPanel",
        "geforce": "{6D809377-6AF0-444B-8957-A3773F02200E}\\NVIDIA Corporation\\NVIDIA GeForce Experience\\NVIDIA GeForce Experience.exe",
        "utorrent": "C:\\Users\\lucky\\AppData\\Roaming\\utorrent\\uTorrent.exe",
        "sound recorder": "Microsoft.WindowsSoundRecorder_8wekyb3d8bbwe!App",
        "whiteboard": "Microsoft.Whiteboard_8wekyb3d8bbwe!Whiteboard",
        "phone link": "Microsoft.YourPhone_8wekyb3d8bbwe!App",
        "remote desktop": "Microsoft.Windows.RemoteDesktop",
        "powershell": "{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe",
        "git bash": "Microsoft.AutoGenerated.{0FDD9C6B-656B-0F1F-AB08-B1CDBB7067B3}",
        "lenovo vantage": "E046963F.LenovoCompanion_k1h2ywk1493x8!App",
        "steelseries": "SteelSeries.Gg.Main",
        "nahimic": "A-Volute.Nahimic_w2gh52qy24etm!App",
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
            "start cmd /k cd ui && npm run dev",
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
        "morning": [
            "chrome",
            "spotify",
            "code .",
        ],
        "coding": [
            "code .",
            "start cmd /k echo Ready to code",
        ],
        "study": [
            "chrome",
            "notepad",
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
