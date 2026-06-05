# ARAXON UI - Tauri + React Frontend

**STEP 11: Complete Tauri + React frontend for ARAXON AI operating system**

This is the desktop UI for ARAXON, connecting to the Python backend via WebSocket at `ws://localhost:8765`.

## Prerequisites

- Node.js 16+ and npm
- Rust 1.60+ (for Tauri builds)
- Python backend running (main.py)

## Setup

```bash
cd ui
npm install
```

## Development

Run the React dev server with Vite (fastest for development):

```bash
npm run dev
```

Opens at `http://localhost:5173` in your browser. Hot-reload enabled.

**Requirements:** Python backend must be running (`python main.py`) with UI WebSocket server active at `ws://localhost:8765`.

## Build Desktop App

Requires Rust toolchain. Build the full Tauri desktop application:

```bash
npm run tauri:build
```

Creates a standalone executable in `src-tauri/target/release/`.

## Development with Tauri

Run Tauri dev mode (includes backend preview):

```bash
npm run tauri:dev
```

## Architecture

### Main Components

- **App.jsx** - Main app logic, WebSocket connection management, state management
- **Sidebar.jsx** - Left navigation (workspace, modes, routines, connect)
- **AIOrb.jsx** - Animated AI orb with waveform visualization
- **SystemMonitor.jsx** - Real-time system stats (CPU, RAM, GPU, NET, DISK, BATTERY)
- **CommandInput.jsx** - Text input and voice controls
- **CommandStream.jsx** - Conversation history and agent task display
- **StatusBar.jsx** - Bottom status bar with uptime and system info

### WebSocket Messages

#### From Python Backend → React

```javascript
// System state updates
{ type: "state", data: { state: "listening|thinking|speaking|standby|processing" } }

// Transcript messages
{ type: "transcript", data: { speaker: "user|araxon", text: "...", timestamp: "..." } }

// Waveform audio levels (32 floats)
{ type: "waveform", data: { levels: [...] } }

// System statistics
{ type: "system_stats", data: { cpu: 0-100, ram: 0-100, gpu: 0-100, net: GB/s, disk: 0-100, battery: 0-100 } }

// Agent execution steps
{ type: "agent_step", data: { step_number: 1, description: "...", status: "running|done|error", done: boolean } }

// System information
{ type: "system_info", data: { ... } }

// Notifications
{ type: "notification", data: { title: "...", message: "...", level: "info|success|warning|error" } }
```

#### From React → Python Backend

```javascript
// Send text command
{ type: "command", data: { text: "..." } }

// Request routine
{ type: "routine", data: { name: "..." } }

// Update settings
{ type: "settings_update", data: { name: "...", value: "..." } }

// Navigation event
{ type: "nav_change", data: { section: "..." } }

// Ping
{ type: "ping" }
```

## Colors (CSS Variables)

All colors are defined as CSS variables in `src/index.css`:

- `--bg-primary`: #080B14 (main background)
- `--bg-sidebar`: #0A0D16 (sidebar background)
- `--bg-card`: #0D1220 (card background)
- `--accent-blue`: #3B82F6 (primary accent)
- `--accent-cyan`: #06B6D4 (cyan accent)
- `--accent-green`: #10B981 (success/online)
- `--text-primary`: #F1F5F9 (main text)
- `--text-secondary`: #94A3B8 (secondary text)
- `--text-muted`: #475569 (muted text)

## Key Features

✅ Real-time WebSocket connection to Python backend  
✅ Animated AI orb with state-based colors  
✅ Live system monitoring with sparkline charts  
✅ Conversation transcript with user/ARAXON messages  
✅ Agent task execution display with step tracking  
✅ Voice command input  
✅ Quick action buttons (Voice, Vision, Terminal, Files, Memory, Automation)  
✅ Sidebar with workspace navigation and mode selection  
✅ Status bar with uptime and system info  
✅ Dark theme matching reference design  
✅ Responsive layout for 1400x820 minimum window  
✅ Auto-reconnect if WebSocket disconnects (every 3s)  

## Running Together

1. **Start Python Backend:**
   ```bash
   python main.py
   ```
   Waits for WebSocket connection, runs main loop

2. **Start React Frontend (in ui/ directory):**
   ```bash
   npm run dev
   ```
   Opens browser to http://localhost:5173
   Connects to ws://localhost:8765

3. **Interact:**
   - Type commands in CommandInput
   - Click quick action buttons
   - Watch system stats update in real-time
   - See agent steps display as tasks execute

## Build for Production

```bash
npm run build          # Build React app
npm run tauri:build    # Build full desktop app
```

Desktop executable output: `src-tauri/target/release/araxon-ui`

## Troubleshooting

**WebSocket connection fails:**
- Ensure Python backend is running: `python main.py`
- Check that port 8765 is not blocked
- Look for "UI ready at ws://localhost:8765" in backend logs

**Styles not applied:**
- Clear browser cache (Ctrl+Shift+Del)
- Hard refresh: Ctrl+Shift+R

**Components not updating:**
- Check browser console for JavaScript errors
- Verify WebSocket messages in Network tab

**Tauri build fails:**
- Ensure Rust is installed: `rustup --version`
- Run `cargo update` in `src-tauri/`

## STEP 12: Final Integration

This completes STEP 11 of ARAXON development. The next step (STEP 12) involves:
- Testing full end-to-end integration
- Performance optimization
- Deployment configuration
- Production hardening
