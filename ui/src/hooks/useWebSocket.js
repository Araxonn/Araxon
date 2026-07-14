import { useEffect } from 'react'
import { useAppStore } from '../store/useAppStore'

const WS_URL = 'ws://localhost:8765'
const RECONNECT_DELAY_MS = 3000
const PING_INTERVAL_MS = 30000

let ws = null
let reconnectTimer = null
let pingTimer = null
let subscriberCount = 0
let intentionalClose = false
let hasLoggedConnectionError = false

const normalizeTranscript = (data) => ({
  role: data.role || (data.speaker === 'user' ? 'user' : 'assistant'),
  text: data.text || '',
  timestamp: data.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  type: data.type,
  items: data.items,
  percent: data.percent,
})

const normalizeWaveform = (data) => {
  if (Array.isArray(data)) return data
  if (Array.isArray(data?.levels)) return data.levels
  return []
}

const normalizeAgentStep = (data) => ({
  index: data.index ?? Math.max(0, (data.step_number || 1) - 1),
  title: data.title || data.description || `Step ${(data.step_number || 1)}`,
  status: data.status || (data.done ? 'done' : 'running'),
  percent: data.percent ?? (data.done ? 100 : 0),
  result: data.result || data.error_message || '',
})

const handleMessage = (event) => {
  const {
    setAraxonState,
    appendTranscript,
    setWaveformLevels,
    setSystemStats,
    appendStatsHistory,
    updateAgentStep,
    setAgentSteps,
    setCodeFile,
    appendCodeSuggestion,
    clearCodeSuggestions,
    setSystemInfo,
    addNotification,
    appendLogLine,
    setMemoryStats,
    setExecutionProgress,
    setIngestedFiles,
    resetLiveData,
    setConnected,
    setAutomationProcesses,
  } = useAppStore.getState()

  try {
    const msg = JSON.parse(event.data)

    switch (msg.type) {
      case 'connection':
        setConnected(true)
        resetLiveData()
        break
      case 'state':
        setAraxonState(msg.data.state)
        break
      case 'transcript':
        appendTranscript(normalizeTranscript(msg.data))
        break
      case 'waveform':
        setWaveformLevels(normalizeWaveform(msg.data))
        break
      case 'system_stats':
        setSystemStats(msg.data)
        Object.entries(msg.data).forEach(([key, value]) => {
          if (!['battery', 'timestamp', 'uptime'].includes(key)) {
            appendStatsHistory(key, value)
          }
        })
        break
      case 'agent_step': {
        const step = normalizeAgentStep(msg.data)
        updateAgentStep(step.index, step)
        break
      }
      case 'agent_steps':
        setAgentSteps((msg.data || []).map(normalizeAgentStep))
        break
      case 'execution_progress':
        setExecutionProgress(msg.data.percent || 0)
        break
      case 'code_update':
        clearCodeSuggestions()
        setCodeFile(msg.data)
        setAraxonState('code')
        break
      case 'code_suggestion':
        appendCodeSuggestion(msg.data)
        break
      case 'system_info':
        setSystemInfo(msg.data)
        break
      case 'notification':
        addNotification({
          id: Math.random(),
          type: msg.data.type || msg.data.level || 'info',
          title: msg.data.title || 'Notification',
          message: msg.data.message || '',
        })
        break
      case 'log_line':
        appendLogLine(msg.data)
        break
      case 'memory_stats':
        setMemoryStats(msg.data)
        break
      case 'ingested_files':
        setIngestedFiles(msg.data.files || [])
        break
      case 'automation_processes':
        setAutomationProcesses(msg.data.processes || [])
        break
      case 'pong':
        setConnected(true)
        break
      default:
        console.log('Unknown message type:', msg.type)
    }
  } catch (err) {
    console.error('WS parse error:', err)
  }
}

const handleOpen = () => {
  hasLoggedConnectionError = false
  useAppStore.getState().setConnected(true)
  clearInterval(pingTimer)
  pingTimer = setInterval(sendPing, PING_INTERVAL_MS)
}

const handleClose = () => {
  useAppStore.getState().setConnected(false)
  clearInterval(pingTimer)
  pingTimer = null
  ws = null

  if (!intentionalClose && subscriberCount > 0) {
    clearTimeout(reconnectTimer)
    reconnectTimer = setTimeout(connect, RECONNECT_DELAY_MS)
  }
}

const handleError = () => {
  if (!hasLoggedConnectionError) {
    hasLoggedConnectionError = true
    console.warn(
      `WebSocket could not connect to ${WS_URL}. Start the ARAXON backend (python main.py) to enable live updates.`
    )
  }
}

const connect = () => {
  if (ws?.readyState === WebSocket.OPEN || ws?.readyState === WebSocket.CONNECTING) {
    return
  }

  try {
    ws = new WebSocket(WS_URL)
    ws.addEventListener('open', handleOpen)
    ws.addEventListener('message', handleMessage)
    ws.addEventListener('close', handleClose)
    ws.addEventListener('error', handleError)
  } catch (err) {
    console.error('Failed to connect:', err)
  }
}

const disconnect = () => {
  intentionalClose = true
  clearTimeout(reconnectTimer)
  clearInterval(pingTimer)
  reconnectTimer = null
  pingTimer = null

  if (ws) {
    ws.removeEventListener('open', handleOpen)
    ws.removeEventListener('message', handleMessage)
    ws.removeEventListener('close', handleClose)
    ws.removeEventListener('error', handleError)
    ws.close()
    ws = null
  }

  useAppStore.getState().setConnected(false)
  intentionalClose = false
}

const send = (payload) => {
  if (ws?.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(payload))
  }
}

export const sendCommand = (text) => send({ type: 'command', data: { text } })
export const sendRoutine = (name) => send({ type: 'routine', data: { name } })
export const sendSettings = (settings) => send({ type: 'settings_update', data: settings })
export const sendNavChange = (nav) => send({ type: 'nav_change', data: { nav } })
export const sendPing = () => send({ type: 'ping' })
export const sendFileIngest = (content, name) =>
  send({ type: 'ingest_file', data: { content, name } })
export const sendMicToggle = (enabled) => send({ type: 'mic_toggle', data: { enabled } })
export const sendVoiceToggle = (enabled) => send({ type: 'voice_toggle', data: { enabled } })
export const sendInterrupt = () => send({ type: 'command', data: { text: 'stop' } })

export const useWebSocket = () => {
  useEffect(() => {
    subscriberCount += 1
    if (subscriberCount === 1) {
      connect()
    }

    return () => {
      subscriberCount -= 1
      if (subscriberCount === 0) {
        disconnect()
      }
    }
  }, [])

  return {
    connected: useAppStore((s) => s.connected),
    sendCommand,
    sendRoutine,
    sendSettings,
    sendNavChange,
    sendPing,
    sendFileIngest,
    sendMicToggle,
    sendVoiceToggle,
    sendInterrupt,
  }
}
