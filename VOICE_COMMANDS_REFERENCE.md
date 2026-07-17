# ARAXON Voice Commands Reference

## Overview
This document lists all voice commands that trigger Araxon automation. Simply speak these commands after saying "Hey Araxon" or the wake word.

---

## 🎯 Workspace Profiles
Launch complete development environments with all tools.

| Command | Action |
|---------|--------|
| "open my mern workspace" | Launches VS Code + npm dev server + localhost:3000 |
| "launch mern" | Same as above |
| "open my python workspace" | Launches VS Code + Python app |
| "launch python" | Same as above |
| "open my ai workspace" | Launches VS Code + Ollama server + localhost:11434 |
| "launch ai" | Same as above |
| "open my focus workspace" | Launches Spotify + VS Code |
| "launch focus" | Same as above |

**Profiles Available:**
- `mern` - Full-stack MERN development
- `python` - Python development
- `ai` - AI/Ollama development
- `focus` - Music + coding (Spotify + VS Code)

---

## 🚀 Application Launcher
Open, launch, or close desktop applications.

| Command | App |
|---------|-----|
| "open spotify" | Launch Spotify |
| "open vs code" | Launch VS Code |
| "open vscode" | Launch VS Code |
| "open chrome" | Launch Google Chrome |
| "open firefox" | Launch Firefox |
| "open discord" | Launch Discord |
| "open slack" | Launch Slack |
| "open terminal" | Open Command Prompt |
| "open notepad" | Open Notepad |
| "open explorer" | Open File Explorer |

**Close Apps:**
| Command | Effect |
|---------|--------|
| "close spotify" | Close Spotify |
| "quit vs code" | Close VS Code |
| "shutdown discord" | Close Discord |

---

## 🌐 Website & Search Navigation

### Open Websites
| Command | Website |
|---------|---------|
| "open youtube" | YouTube |
| "open github" | GitHub |
| "open google" | Google |
| "open stackoverflow" | Stack Overflow |
| "open gmail" | Gmail |
| "open reddit" | Reddit |
| "open twitter" | Twitter |
| "open linkedin" | LinkedIn |
| "open chatgpt" | ChatGPT |
| "open localhost" | http://localhost:3000 |

### Search Commands
| Command | Effect |
|---------|--------|
| "search google [query]" | Search Google for query |
| "search for [query]" | Same as above |
| "search youtube [query]" | Search YouTube |
| "play on youtube [query]" | Search YouTube |
| "go to [website]" | Navigate to website |
| "navigate to [website]" | Navigate to website |

---

## 💻 Terminal Commands

| Command | Effect |
|---------|--------|
| "run server" | Run: `npm run dev` |
| "start server" | Run: `npm run dev` |
| "run python" | Run: `python main.py` |
| "install packages" | Run: `pip install -r requirements.txt` |
| "git status" | Run: `git status` |
| "git push" | Run: `git push` |
| "run tests" | Run: `pytest` |
| "run [any command]" | Execute custom command safely |

---

## 🛠️ System Controls

| Command | Effect |
|---------|--------|
| "help" | List all available commands |
| "what can you do" | List all available commands |
| "what commands do you support" | List all available commands |
| "sleep" | Enter standby mode |
| "go to sleep" | Enter standby mode |
| "standby" | Enter standby mode |
| "goodbye" | Enter standby mode |
| "stop" | Interrupt current action |
| "cancel" | Cancel current action |
| "abort" | Cancel current action |
| "never mind" | Cancel current action |

---

## 📸 Vision & Screenshot

| Command | Effect |
|---------|--------|
| "take screenshot" | Capture current page/screen |

---

## 💾 Memory & Learning

| Command | Effect |
|---------|--------|
| "remember that [info]" | Save to long-term memory |
| "don't forget [info]" | Save to long-term memory |
| "recall" | Retrieve relevant memories |
| "recall [topic]" | Retrieve memories about topic |
| "what do you remember" | Retrieve relevant memories |
| "ingest my files" | Process and ingest files into RAG |

---

## 🎤 Wake Words

Trigger Araxon by saying:
- "Hey Araxon"
- "Araxon"
- "Ok Araxon"
- "Wake up Araxon"

---

## 📋 Notes

- **Fuzzy Matching**: Commands use fuzzy matching, so slight pronunciation variations are accepted
  - "spi Spotify" → recognized as "open spotify"
  - "open my mern" → launches mern workspace
  
- **Always Available**: All workspace, app, website, and search commands work in **ACTIVE** mode after waking Araxon

- **Sleep/Standby**: Once in standby, only wake words will trigger commands. Say "Hello Araxon" to wake up.

- **Custom Commands**: You can say "run [any command]" to execute terminal commands (restricted to safe executables: npm, python, pip, git, node, uvicorn, pytest, ls, dir)

---

## 🔧 Current Configuration

**Apps Supported:**
- vs code, vscode, terminal, spotify, chrome, firefox, explorer, notepad, discord, slack

**Websites:**
- youtube, github, google, stackoverflow, gmail, reddit, twitter, linkedin, chatgpt, localhost

**Workspaces:**
- mern, python, ai, focus

**Commands:**
- run server, start server, run python, install packages, git status, git push, run tests

---

## 💡 Quick Examples

1. **"Hey Araxon, open my mern workspace"**
   → Launches full MERN stack environment

2. **"Araxon, search google what is machine learning"**
   → Searches Google for machine learning

3. **"Ok Araxon, open spotify"**
   → Launches Spotify (via web if desktop app unavailable)

4. **"Araxon, run npm install"**
   → Executes `npm install` safely

5. **"Araxon, remember that the database password is 12345"**
   → Saves to long-term memory for later recall

---

## 🚀 Getting Started

1. Say the wake word: **"Hey Araxon"**
2. Wait for confirmation: **"I'm listening."**
3. Say your command (see examples above)
4. Araxon will respond with the result

---

**Last Updated:** July 2, 2026
