# 🚀 ARAXON

<div align="center">

[![Python Version](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Code Style](https://img.shields.io/badge/Code%20Style-Black-black?style=flat-square)](https://github.com/psf/black)
[![Async](https://img.shields.io/badge/Async-First-ff69b4?style=flat-square)](https://docs.python.org/3/library/asyncio.html)
[![Status](https://img.shields.io/badge/Status-Active%20Development-orange?style=flat-square)]()

**A Futuristic Modular AI Operating System Built in Python**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Environment Setup](#-environment-setup)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [API Integration](#-api-integration)
- [Configuration](#-configuration)
- [Screenshots](#-screenshots)
- [Development](#-development)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)
- [Author](#-author)

---

## 🎯 Overview

**ARAXON** is an advanced modular AI operating system that integrates multiple AI capabilities into a cohesive, scalable platform. It combines voice interaction, computer vision, persistent memory, automation capabilities, and autonomous agents into a single, extensible framework.

Whether you're building an AI assistant, automating workflows, or exploring advanced AI capabilities, ARAXON provides a production-ready foundation with professional-grade architecture.

### Key Highlights
- 🎙️ **Voice-First Interaction**: Natural language processing with speech recognition and synthesis
- 👁️ **Computer Vision**: Advanced image processing and object detection
- 🧠 **Persistent Memory**: Vector-based knowledge base with semantic search
- 🤖 **Autonomous Agents**: Multi-agent system with advanced decision making
- 🔄 **Automation**: Workflow orchestration and task automation
- 🌐 **Internet Integration**: Web browsing, API access, and data extraction
- ⚡ **Async-First**: Built on Python asyncio for high-performance concurrent operations
- 🎨 **Beautiful UI**: Modern React-based interface with Tauri desktop integration

---

## ✨ Features

### Voice Capabilities
- 🎙️ Speech-to-text with Faster-Whisper
- 🔊 Text-to-speech synthesis
- 👂 Wake word detection and voice activation
- 🎯 Natural language understanding

### Vision & Processing
- 📸 Real-time screenshot capture
- 🔍 Optical Character Recognition (OCR)
- 👁️ Computer vision analysis
- 🎬 Video processing and streaming

### Memory & Knowledge
- 📚 Vector database with ChromaDB
- 🧠 Semantic search capabilities
- 💾 Long-term knowledge storage
- 📖 Document ingestion and processing
- 🔗 Knowledge graph integration

### Automation & Agents
- 🤖 Multi-agent orchestration
- 📋 Task automation workflows
- ⏱️ Intelligent scheduling
- 🎯 Goal-oriented execution
- 📊 Agent performance monitoring

### Internet & Data
- 🌍 Web browsing automation
- 🔗 API integration
- 📰 News aggregation
- 🔎 Intelligent web search
- 📰 Content extraction and analysis

### User Interface
- 🎨 Modern React dashboard
- 💻 Tauri desktop application
- 🌐 WebSocket real-time communication
- 📱 Responsive design
- 🎯 Intuitive command interface

---

## 🛠️ Tech Stack

### Backend
- **Python 3.11+** - Core runtime
- **LangChain** - AI orchestration framework
- **LangGraph** - Agent and workflow execution
- **Groq & Ollama** - LLM providers
- **ChromaDB** - Vector database
- **Faster-Whisper** - Speech recognition
- **Kokoro** - Text-to-speech synthesis

### Processing & ML
- **PyTorch** - Deep learning framework
- **Sentence Transformers** - Embedding models
- **OpenCV** - Computer vision
- **Tesseract** - OCR engine
- **NumPy** - Numerical computing

### Frontend & UI
- **React 18+** - UI framework
- **Tauri** - Desktop application
- **Vite** - Build tool
- **WebSockets** - Real-time communication
- **CSS3** - Styling

### Infrastructure
- **asyncio** - Asynchronous programming
- **Pydantic** - Data validation
- **Loguru** - Logging framework
- **python-dotenv** - Environment management

---

## 📁 Project Structure

```
ARAXON/
├── araxon/                          # Main package
│   ├── __init__.py
│   ├── core/                        # Core infrastructure
│   │   ├── config.py                # Configuration management
│   │   ├── logger.py                # Logging system
│   │   └── utils.py                 # Utility functions
│   │
│   ├── ai/                          # AI integration
│   │   ├── brain.py                 # Core AI reasoning
│   │   ├── router.py                # Request routing
│   │   ├── memory.py                # AI memory management
│   │   └── personality.py           # AI personality traits
│   │
│   ├── voice/                       # Voice I/O
│   │   ├── listener.py              # Speech input
│   │   ├── synthesizer.py           # Speech output
│   │   ├── transcriber.py           # Audio transcription
│   │   ├── audio_player.py          # Audio playback
│   │   └── voice_*.py               # Voice utilities
│   │
│   ├── vision/                      # Computer vision
│   │   ├── analyzer.py              # Image analysis
│   │   ├── screenshot.py            # Screenshot capture
│   │   ├── ocr.py                   # Optical character recognition
│   │   ├── vision_pipeline.py       # Processing pipeline
│   │   └── vision_router.py         # Vision routing
│   │
│   ├── memory/                      # Knowledge & memory system
│   │   ├── embedder.py              # Embedding generation
│   │   ├── vector_store.py          # Vector database wrapper
│   │   ├── long_term_memory.py      # Persistent memory
│   │   ├── file_ingester.py         # Document processing
│   │   └── rag_pipeline.py          # RAG implementation
│   │
│   ├── automation/                  # Task automation
│   │   ├── automation_router.py     # Request routing
│   │   ├── app_launcher.py          # Application launching
│   │   ├── command_runner.py        # Command execution
│   │   ├── browser_agent.py         # Browser automation
│   │   └── workspace_manager.py     # Workspace management
│   │
│   ├── agent/                       # Agent system
│   │   ├── agent_controller.py      # Agent orchestration
│   │   ├── executor.py              # Task execution
│   │   ├── planner.py               # Planning & reasoning
│   │   ├── graph.py                 # Agent graph
│   │   └── tools.py                 # Agent tools
│   │
│   ├── internet/                    # Internet integration
│   │   ├── internet_router.py       # Request routing
│   │   ├── searcher.py              # Web search
│   │   ├── news_fetcher.py          # News aggregation
│   │   ├── researcher.py            # Research capabilities
│   │   ├── wiki_lookup.py           # Wikipedia integration
│   │   └── extractor.py             # Content extraction
│   │
│   └── ui/                          # User interface
│       ├── ui_bridge.py             # Frontend bridge
│       └── websocket_server.py      # Real-time communication
│
├── ui/                              # Frontend application
│   ├── src/                         # React source
│   │   ├── components/              # UI components
│   │   ├── App.jsx                  # Main app
│   │   └── main.jsx                 # Entry point
│   ├── src-tauri/                   # Tauri backend
│   ├── package.json                 # Frontend dependencies
│   └── vite.config.js               # Build configuration
│
├── config/                          # Configuration
│   └── settings.yaml                # Settings file
│
├── data/                            # Data storage
│   ├── chromadb/                    # Vector database
│   └── ingested/                    # Processed documents
│
├── logs/                            # Application logs
│   └── screenshots/                 # Captured screenshots
│
├── models/                          # AI models
│   └── models--*                    # Model cache
│
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── setup_project.py                 # Project initialization
├── .env.example                     # Environment template
├── README.md                        # Documentation
├── LICENSE                          # License file
└── .gitignore                       # Git ignore rules

```

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

### System Requirements
- **OS**: Windows 10/11, macOS 11+, or Linux (Ubuntu 20.04+)
- **Python**: 3.11 or higher
- **Node.js**: 16+ (for frontend development)
- **RAM**: Minimum 8GB (16GB recommended for ML models)
- **GPU**: NVIDIA GPU recommended (CUDA 11.8+) for faster inference

### Software Requirements
- Git
- pip (Python package manager)
- FFmpeg (for audio processing)
- Tesseract OCR (for document processing)

### Optional but Recommended
- Ollama (for local LLM inference)
- Groq API key (for cloud LLM access)
- Chromium/Chrome (for browser automation)

---

## 🔧 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/araxon.git
cd araxon
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv .venv311
.venv311\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv .venv311
source .venv311/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Step 4: Install System Dependencies

**Windows (PowerShell as Admin):**
```powershell
# Install FFmpeg
choco install ffmpeg -y

# Install Tesseract OCR
choco install tesseract -y

# Optional: Install Ollama
choco install ollama -y
```

**macOS:**
```bash
# Install FFmpeg
brew install ffmpeg

# Install Tesseract OCR
brew install tesseract

# Optional: Install Ollama
brew install ollama
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y ffmpeg tesseract-ocr
# Optional: Install Ollama (https://ollama.ai)
```

### Step 5: Setup Frontend (Optional)

If you want to develop the UI:

```bash
cd ui
npm install
npm run build  # or npm run dev for development
```

---

## 🌍 Environment Setup

### Create `.env` File

Copy the provided `.env.example` file:

```bash
cp .env.example .env
```

### Required Environment Variables

```env
# Application Settings
APP_NAME=ARAXON
DEBUG_MODE=False
LOG_LEVEL=INFO

# API Keys
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional

# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral  # or llama2, neural-chat, etc.

# Voice Configuration
WAKE_WORD=araxon
TTS_MODEL=kokoro  # or tts-1, etc.
SPEECH_RECOGNITION_LANGUAGE=en-US

# Memory Configuration
CHROMA_DB_PATH=./data/chromadb
VECTOR_STORE_TYPE=chroma

# Database
DATABASE_URL=sqlite:///./data/araxon.db

# UI Configuration
UI_HOST=localhost
UI_PORT=5173
WEBSOCKET_PORT=8765

# Optional: LLM Provider Selection
LLM_PROVIDER=groq  # options: groq, ollama, openai

# Optional: Vision Configuration
VISION_MODEL=gpt-4-vision  # or local model
OCR_LANGUAGE=eng
```

### Getting API Keys

**Groq API Key:**
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Create an API key
4. Add to your `.env` file

**OpenAI API Key (Optional):**
1. Visit [platform.openai.com](https://platform.openai.com)
2. Create an account
3. Generate API key
4. Add to your `.env` file

---

## 🚀 Quick Start

### Basic Setup (Automated)

```bash
# Activate virtual environment first
.venv311\Scripts\activate  # Windows
# or
source .venv311/bin/activate  # macOS/Linux

# Run setup script
python setup_project.py

# Start ARAXON
python main.py
```

### Running the Application

**Terminal 1 - Backend:**
```bash
.venv311\Scripts\python.exe main.py
```

**Terminal 2 - Frontend (Optional):**
```bash
cd ui
npm run dev
```

The application will:
1. Initialize all subsystems
2. Load configuration from `.env`
3. Connect to vector database
4. Initialize voice and vision pipelines
5. Start the web server
6. Begin listening for voice commands

---

## 💬 Usage

### Via Command Line

```bash
python main.py
```

Then interact with ARAXON:
- **Voice**: Speak your wake word followed by a command
- **CLI**: Type commands directly in the terminal
- **Web UI**: Access the dashboard at `http://localhost:5173`

### Example Commands

```python
# Voice Command
"Araxon, search for Python tutorials"
"Araxon, take a screenshot"
"Araxon, what time is it?"

# Terminal Command
python main.py --command "search python tutorials"
python main.py --voice-only
```

### Via Python API

```python
import asyncio
from araxon.ai import ARAXONBrain
from araxon.agent import AgentController

async def main():
    # Initialize brain
    brain = ARAXONBrain()
    
    # Process a query
    response = await brain.process("What is AI?")
    print(response)
    
    # Interact with agents
    agent = AgentController()
    result = await agent.execute_task("Search for recent AI news")
    print(result)

asyncio.run(main())
```

---

## 🔌 API Integration

### REST Endpoints

ARAXON exposes several REST APIs:

#### Brain Endpoint
```
POST /api/brain/think
Content-Type: application/json

{
  "query": "What is machine learning?",
  "context": "optional_context"
}

Response: { "response": "...", "confidence": 0.95 }
```

#### Vision Endpoint
```
POST /api/vision/analyze
Content-Type: multipart/form-data

File: image.png

Response: { "analysis": "...", "objects": [...] }
```

#### Memory Endpoint
```
POST /api/memory/query
Content-Type: application/json

{
  "query": "Find documents about Python",
  "limit": 10
}

Response: { "results": [...], "total": 42 }
```

#### Agent Endpoint
```
POST /api/agent/execute
Content-Type: application/json

{
  "task": "Automate daily report generation",
  "parameters": {...}
}

Response: { "status": "completed", "result": "..." }
```

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8765');

ws.onmessage = (event) => {
  console.log('Message from ARAXON:', event.data);
};

ws.send(JSON.stringify({
  type: 'command',
  data: 'your command here'
}));
```

---

## ⚙️ Configuration

### Core Configuration (`araxon/core/config.py`)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "ARAXON"
    DEBUG_MODE: bool = False
    LOG_LEVEL: str = "INFO"
    
    # LLM Settings
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True
```

### Logger Configuration

```python
from araxon.core.logger import logger

logger.info("Application started")
logger.debug("Debug information")
logger.error("An error occurred")
logger.warning("Warning message")
```

### Custom Settings

Edit `config/settings.yaml`:

```yaml
application:
  name: ARAXON
  version: 1.0.0
  
ai:
  model: mistral
  temperature: 0.7
  
voice:
  wake_word: araxon
  language: en-US
  
memory:
  vector_dimension: 1536
  top_k: 10
```

---

## 📸 Screenshots

### Dashboard
```
[Screenshot placeholder - Update with actual dashboard screenshot]
```

### Voice Command Interface
```
[Screenshot placeholder - Update with actual UI screenshot]
```

### Vision Analysis
```
[Screenshot placeholder - Update with actual vision output screenshot]
```

### Agent Execution
```
[Screenshot placeholder - Update with actual agent output screenshot]
```

> 💡 **Tip**: Replace these placeholders with actual screenshots of your application

---

## 👨‍💻 Development

### Project Structure Philosophy

ARAXON follows these principles:

1. **Modularity**: Each subsystem is independent
2. **Async-First**: All I/O operations use async/await
3. **Configuration**: Settings via environment variables
4. **Logging**: Comprehensive logging with loguru
5. **Testing**: Dedicated test files for each module

### Adding a New Module

1. Create a new folder in `araxon/`
2. Add `__init__.py` with module exports
3. Implement your module with async functions
4. Register in `main.py` initialization
5. Add tests in `tests/`

Example:

```python
# araxon/my_module/__init__.py
from .my_module import MyModuleClass

__all__ = ["MyModuleClass"]

# Usage in main.py
from araxon.my_module import MyModuleClass

async def initialize():
    my_module = MyModuleClass()
    await my_module.setup()
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_core.py

# Run with coverage
pytest --cov=araxon tests/
```

### Code Style

ARAXON uses:
- **Black** for formatting
- **Flake8** for linting
- **MyPy** for type checking

```bash
# Format code
black araxon/

# Lint
flake8 araxon/

# Type check
mypy araxon/
```

---

## 🗺️ Roadmap

### ✅ Completed (Phase 1)
- Foundation infrastructure
- Configuration management
- Logging system
- Core utilities

### 🚀 In Progress (Phase 2)
- Advanced voice capabilities
- Vision pipeline optimization
- Memory system enhancement
- UI/UX improvements

### 📋 Planned (Phase 3-5)
- Multi-language support
- Enhanced security features
- Mobile app version
- Cloud synchronization
- Plugin system
- Performance optimization

### 🔮 Future Vision (Phase 6+)
- Full voice AI assistant
- Advanced reasoning capabilities
- Custom model training
- Enterprise features
- API marketplace

See [PROJECT_CHECKLIST.md](PROJECT_CHECKLIST.md) for detailed progress.

---

## 🤝 Contributing

We welcome contributions! Here's how to help:

### Code of Conduct

Please note we have a [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming community.

### Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Write tests for new functionality
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Write docstrings for all functions
- Add type hints
- Include unit tests (minimum 80% coverage)
- Update documentation
- Use conventional commit messages

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(vision): add image recognition capability

Implemented ResNet-based image classification with
confidence scoring and bounding box detection.

Closes #123
```

### Pull Request Process

1. Update `README.md` if needed
2. Update `CHANGELOG.md` with changes
3. Ensure tests pass: `pytest`
4. Request review from maintainers
5. Address feedback and iterate

---

## 🐛 Troubleshooting

### Common Issues

#### Issue: `ModuleNotFoundError: No module named 'araxon'`

**Solution:**
```bash
# Ensure virtual environment is activated
.venv311\Scripts\activate  # Windows
source .venv311/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

#### Issue: `GROQ_API_KEY not found`

**Solution:**
```bash
# Check .env file exists and is readable
cat .env  # or type .env on Windows

# Get API key from https://console.groq.com
# Add to .env:
GROQ_API_KEY=your_key_here
```

#### Issue: Microphone not working

**Solution:**
```bash
# Check device permissions
# Verify audio device:
python -c "import sounddevice; print(sounddevice.query_devices())"

# Reinstall audio libraries
pip install --upgrade sounddevice numpy
```

#### Issue: GPU not detected for PyTorch

**Solution:**
```bash
# Check CUDA installation
python -c "import torch; print(torch.cuda.is_available())"

# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Issue: Vector database errors

**Solution:**
```bash
# Reset vector database
rm -rf data/chromadb/*

# Reinitialize
python -c "from araxon.memory import LongTermMemory; m = LongTermMemory(); m.initialize()"
```

### Debug Mode

Enable detailed logging:

```bash
# Via command line
DEBUG_MODE=True LOG_LEVEL=DEBUG python main.py

# Or in .env
DEBUG_MODE=True
LOG_LEVEL=DEBUG
```

### Getting Help

- 📖 Check [INSTALLATION.md](INSTALLATION.md)
- 📋 Review [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- 💬 Open an [Issue](https://github.com/yourusername/araxon/issues)
- 📞 Contact the maintainers

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive open-source license that allows you to:
- ✅ Use commercially
- ✅ Modify the software
- ✅ Distribute the software
- ✅ Use privately
- ❌ Hold liable

**With the requirement:**
- 📋 Include license and copyright notice

For more information, visit [opensource.org/licenses/MIT](https://opensource.org/licenses/MIT)

---

## 👤 Author

**ARAXON Development Team**

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com
- Website: [your-website.com](https://your-website.com)

### Contributing Authors
- [Contributor 1](https://github.com/contributor1) - Feature/Module contributions
- [Contributor 2](https://github.com/contributor2) - Bug fixes and improvements

### Acknowledgments

Special thanks to:
- The Python community
- LangChain team for excellent framework
- All contributors and supporters
- Open-source projects we depend on

---

## 📞 Support & Community

- 🐛 **Report Bugs**: [GitHub Issues](https://github.com/yourusername/araxon/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/yourusername/araxon/discussions)
- 📚 **Documentation**: [Wiki](https://github.com/yourusername/araxon/wiki)
- 💬 **Community Chat**: [Discord](https://discord.gg/your-server)
- 🤝 **Join Us**: [Contributing Guide](CONTRIBUTING.md)

---

## 📊 Project Statistics

- **Language**: Python 3.11+
- **License**: MIT
- **Repository**: [GitHub](https://github.com/yourusername/araxon)
- **Status**: Active Development 🚀
- **Last Updated**: May 2024

---

## 🔐 Security

For security concerns, please email: security@your-domain.com

Do not open security vulnerabilities publicly. Please follow responsible disclosure practices.

---

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

### Latest Release
- Version: 1.0.0
- Released: May 2024
- [Release Notes](https://github.com/yourusername/araxon/releases/tag/v1.0.0)

---

<div align="center">

**Made with ❤️ by the ARAXON Team**

[⭐ Star us on GitHub](https://github.com/yourusername/araxon) | [🐦 Follow us on Twitter](https://twitter.com/araxon) | [📧 Newsletter](https://your-newsletter.com)

</div>

---

**Last Updated**: May 24, 2024  
**Documentation Version**: 1.0.0  
**Status**: ✅ Maintained
