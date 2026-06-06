import React, { useState, useEffect, useRef, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import AIOrb from './components/AIOrb'
import VoiceWaveform from './components/VoiceWaveform'
import SystemMonitor from './components/SystemMonitor'
import CommandInput from './components/CommandInput'
import CommandStream from './components/CommandStream'
import StatusBar from './components/StatusBar'
import './App.css'

export default function App() {
  // Main state
  const [araxonState, setAraxonState] = useState('standby')
  const [transcript, setTranscript] = useState([])
  const [agentSteps, setAgentSteps] = useState([])
  const [waveformLevels, setWaveformLevels] = useState(Array(32).fill(0))
  const [systemStats, setSystemStats] = useState({
    cpu: 0,
    ram: 0,
    gpu: 0,
    net: 0,
    disk: 0,
    battery: 0,
  })
  const [systemInfo, setSystemInfo] = useState({})
  const [activeTab, setActiveTab] = useState('Commands')
  const [activeMode, setActiveMode] = useState('Assist Mode')
  const [activeNav, setActiveNav] = useState('Dashboard')
  const [notifications, setNotifications] = useState([])
  const [connected, setConnected] = useState(false)
  const [startTime, setStartTime] = useState(Date.now())

  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const systemStatsHistoryRef = useRef({})

  // Initialize system stats history
  useEffect(() => {
    systemStatsHistoryRef.current = {
      cpu: [],
      ram: [],
      gpu: [],
      net: [],
      disk: [],
      battery: [],
    }
  }, [])

  // Connect to WebSocket
  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    try {
      const ws = new WebSocket('ws://localhost:8765')

      ws.onopen = () => {
        console.log('Connected to ARAXON WebSocket')
        setConnected(true)
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current)
        }
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          handleWebSocketMessage(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnected(false)
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setConnected(false)
        // Attempt to reconnect in 3 seconds
        reconnectTimeoutRef.current = setTimeout(connectWebSocket, 3000)
      }

      wsRef.current = ws
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      setConnected(false)
      reconnectTimeoutRef.current = setTimeout(connectWebSocket, 3000)
    }
  }, [])

  // Handle incoming WebSocket messages
  const handleWebSocketMessage = (message) => {
    const { type, data } = message

    switch (type) {
      case 'state':
        setAraxonState(data.state || 'standby')
        break

      case 'transcript':
        setTranscript((prev) => {
          const updated = [
            ...prev,
            {
              id: `transcript-${Date.now()}-${Math.random()}`,
              speaker: data.speaker,
              text: data.text,
              timestamp: data.timestamp,
            },
          ]
          // Keep only last 100 entries
          if (updated.length > 100) {
            return updated.slice(-100)
          }
          return updated
        })
        break

      case 'waveform':
        setWaveformLevels(data.levels || Array(32).fill(0))
        break

      case 'system_stats':
        setSystemStats({
          cpu: data.cpu || 0,
          ram: data.ram || 0,
          gpu: data.gpu || 0,
          net: data.net || 0,
          disk: data.disk || 0,
          battery: data.battery || 0,
        })
        // Store history for sparklines
        Object.keys(systemStatsHistoryRef.current).forEach((key) => {
          const history = systemStatsHistoryRef.current[key]
          const value = data[key] || 0
          history.push(value)
          if (history.length > 20) {
            history.shift()
          }
        })
        break

      case 'agent_step':
        setAgentSteps((prev) => {
          const stepIndex = prev.findIndex((s) => s.step_number === data.step_number)
          if (stepIndex >= 0) {
            const updated = [...prev]
            updated[stepIndex] = {
              ...updated[stepIndex],
              ...data,
            }
            return updated
          }
          return [...prev, data]
        })
        break

      case 'system_info':
        setSystemInfo(data)
        break

      case 'notification':
        const notifId = `notif-${Date.now()}`
        setNotifications((prev) => [...prev, { id: notifId, ...data }])
        // Auto-dismiss after 4 seconds
        setTimeout(() => {
          setNotifications((prev) => prev.filter((n) => n.id !== notifId))
        }, 4000)
        break

      case 'connection':
        console.log('Connected to ARAXON backend')
        break

      default:
        console.log('Unknown message type:', type)
    }
  }

  // Connect on mount
  useEffect(() => {
    connectWebSocket()
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [connectWebSocket])

  // Send command to backend
  const sendCommand = useCallback((text) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'command',
          data: { text },
        })
      )
    }
  }, [])

  return (
    <div className="app-container">
      {!connected && (
        <div className="connection-overlay">
          <div className="connection-message">
            <div className="orb-connecting"></div>
            <p>Connecting to ARAXON...</p>
          </div>
        </div>
      )}

      <Sidebar activeNav={activeNav} setActiveNav={setActiveNav} activeMode={activeMode} setActiveMode={setActiveMode} />

      <main className="main-content">
        <div className="greeting-section">
          <h1>
            Hello, <span className="accent">User</span>
          </h1>
          <p>I'm listening. How can I assist you today?</p>
          <div className="greeting-actions">
            <button aria-label="Expand">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="15 3 21 3 21 9"></polyline>
                <polyline points="9 21 3 21 3 15"></polyline>
                <line x1="21" y1="3" x2="3" y2="21"></line>
              </svg>
            </button>
            <button aria-label="Minimize">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
            </button>
            <button aria-label="Settings">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M12 1v6m0 6v6M4.22 4.22l4.24 4.24m6.08 0l4.24-4.24M1 12h6m6 0h6M4.22 19.78l4.24-4.24m6.08 0l4.24 4.24"></path>
              </svg>
            </button>
            <button aria-label="Sound">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                <path d="M15.54 8.46a7 7 0 0 1 0 9.9M19.07 4.93a11 11 0 0 1 0 15.66"></path>
              </svg>
            </button>
          </div>
        </div>

        <div className="center-panel">
          <AIOrb state={araxonState} waveformLevels={waveformLevels} />

          <div className="quick-actions">
            <button className="action-btn" title="Voice">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"></path>
                <path d="M17 16.91c-1.48 1.45-3.76 2.36-6 2.36s-4.52-.91-6-2.36m12-2.02h1.97c0 2.5-1.6 4.63-3.8 5.68V23h-2v-4.07c-.6-.34-1.15-.77-1.65-1.27M3 9h4V5H3v4z"></path>
              </svg>
              <span>Voice</span>
            </button>
            <button className="action-btn" title="Vision">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"></path>
              </svg>
              <span>Vision</span>
            </button>
            <button className="action-btn" title="Terminal">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"></path>
              </svg>
              <span>Terminal</span>
            </button>
            <button className="action-btn" title="Files">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"></path>
              </svg>
              <span>Files</span>
            </button>
            <button className="action-btn" title="Memory">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"></path>
              </svg>
              <span>Memory</span>
            </button>
            <button className="action-btn" title="Automation">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"></path>
              </svg>
              <span>Automation</span>
            </button>
          </div>

          <SystemMonitor stats={systemStats} history={systemStatsHistoryRef.current} />

          <CommandInput onSendCommand={sendCommand} />
        </div>

        <CommandStream
          transcript={transcript}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          agentSteps={agentSteps}
          state={araxonState}
        />
      </main>

      <StatusBar startTime={startTime} />

      {/* Notification container */}
      <div className="notifications">
        {notifications.map((notif) => (
          <div key={notif.id} className={`notification notification-${notif.level}`}>
            <strong>{notif.title}</strong>
            <p>{notif.message}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
