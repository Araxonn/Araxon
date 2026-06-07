import React from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useWebSocket } from '../../hooks/useWebSocket'
import { useUptime } from '../../hooks/useUptime'
import { Mic, MicOff, Volume2, Cpu } from 'lucide-react'
import { Button } from '../ui/button'

const StatusBar = () => {
  const {
    micEnabled,
    voiceEnabled,
    toggleMic,
    toggleVoice,
    systemStats,
    setMemoryPanelOpen,
  } = useAppStore()

  const { sendMicToggle, sendVoiceToggle } = useWebSocket()
  const { formattedUptime } = useUptime()

  const handleMicToggle = () => {
    toggleMic()
    sendMicToggle(!micEnabled)
  }

  const handleVoiceToggle = () => {
    toggleVoice()
    sendVoiceToggle(!voiceEnabled)
  }

  const getMemColor = () => {
    const ram = systemStats.ram || 0
    if (ram > 90) return 'text-arx-red'
    if (ram > 70) return 'text-arx-orange'
    return 'text-arx-green'
  }

  return (
    <div className="h-10 bg-arx-bg border-t border-arx-border flex items-center justify-between px-4 text-xs font-mono text-arx-muted">
      {/* Left section */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="sm"
          className={`h-6 px-2 text-xs flex items-center gap-1 ${
            micEnabled
              ? 'text-arx-green hover:text-arx-green'
              : 'text-arx-red hover:text-arx-red'
          }`}
          onClick={handleMicToggle}
        >
          {micEnabled ? <Mic size={12} /> : <MicOff size={12} />}
          <span>Mic: {micEnabled ? 'On' : 'Off'}</span>
        </Button>

        <Button
          variant="ghost"
          size="sm"
          className={`h-6 px-2 text-xs flex items-center gap-1 ${
            voiceEnabled
              ? 'text-arx-green hover:text-arx-green'
              : 'text-arx-red hover:text-arx-red'
          }`}
          onClick={handleVoiceToggle}
        >
          <Volume2 size={12} />
          <span>Voice: {voiceEnabled ? 'On' : 'Off'}</span>
        </Button>

        <Button
          variant="ghost"
          size="sm"
          className={`h-6 px-2 text-xs flex items-center gap-1 ${getMemColor()}`}
          onClick={() => setMemoryPanelOpen(true)}
        >
          <Cpu size={12} />
          <span>Mem: {systemStats.ram || 0}%</span>
        </Button>
      </div>

      {/* Center section */}
      <div className="text-arx-secondary">{formattedUptime}</div>

      {/* Right section */}
      <div className="text-arx-secondary">Uptime</div>
    </div>
  )
}

export default StatusBar
