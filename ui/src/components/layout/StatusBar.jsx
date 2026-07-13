import React from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useWebSocket } from '../../hooks/useWebSocket'
import { useUptime } from '../../hooks/useUptime'
import { Mic, MicOff, Volume2, Cpu } from 'lucide-react'
import { Button } from '../ui/button'
import VoiceWaveform from '../orb/VoiceWaveform'

const StatusBar = () => {
  const {
    micEnabled,
    voiceEnabled,
    toggleMic,
    toggleVoice,
    systemStats,
    setMemoryPanelOpen,
    araxonState,
    connected,
  } = useAppStore()

  const { sendMicToggle, sendVoiceToggle } = useWebSocket()
  const { formattedUptime } = useUptime()
  const uptimeLabel = systemStats.uptime || formattedUptime

  const handleMicToggle = () => {
    const next = !micEnabled
    toggleMic()
    sendMicToggle(next)
  }

  const handleVoiceToggle = () => {
    const next = !voiceEnabled
    toggleVoice()
    sendVoiceToggle(next)
  }

  const getMemColor = () => {
    const ram = systemStats.ram || 0
    if (ram > 90) return 'text-arx-red'
    if (ram > 70) return 'text-arx-orange'
    return 'text-arx-green'
  }

  const getStateLabel = () => {
    switch (araxonState) {
      case 'executing':
        return 'Araxon is executing...'
      case 'code':
        return 'Code mode active'
      case 'thinking':
        return 'Araxon is thinking...'
      default:
        return 'Araxon is listening...'
    }
  }

  return (
    <div className="h-9 bg-arx-sidebar border-t border-arx-border flex items-center justify-between px-4 text-[11px] text-arx-muted shrink-0">
      <div className="flex items-center gap-2 min-w-0">
        <div className="flex items-center gap-1.5">
          <div
            className={`w-1.5 h-1.5 rounded-full ${
              connected ? 'bg-arx-green shadow-[0_0_6px_#10B981]' : 'bg-arx-orange'
            }`}
          />
          <span className={connected ? 'text-arx-green font-semibold' : 'text-arx-orange'}>
            ONLINE
          </span>
        </div>
        <span className="text-arx-border">|</span>
        <span className="text-arx-secondary">Araxon Core: Active</span>
      </div>

      <div className="text-arx-secondary font-mono">
        Uptime: <span className="text-arx-text">{uptimeLabel}</span>
      </div>

      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="sm"
          className={`h-6 px-1.5 text-[11px] gap-1 ${
            micEnabled ? 'text-arx-secondary hover:text-arx-text' : 'text-arx-red'
          }`}
          onClick={handleMicToggle}
        >
          {micEnabled ? <Mic size={11} /> : <MicOff size={11} />}
          Mic: {micEnabled ? 'On' : 'Off'}
        </Button>

        <Button
          variant="ghost"
          size="sm"
          className={`h-6 px-1.5 text-[11px] gap-1 ${
            voiceEnabled ? 'text-arx-secondary hover:text-arx-text' : 'text-arx-red'
          }`}
          onClick={handleVoiceToggle}
        >
          <Volume2 size={11} />
          Voice: {voiceEnabled ? 'On' : 'Off'}
        </Button>

        {voiceEnabled && (
          <div className="w-12 h-4 overflow-hidden opacity-60">
            <VoiceWaveform compact />
          </div>
        )}

        <Button
          variant="ghost"
          size="sm"
          className={`h-6 px-1.5 text-[11px] gap-1 ${getMemColor()}`}
          onClick={() => setMemoryPanelOpen(true)}
        >
          <Cpu size={11} />
          Mem: {systemStats.ram || 0}%
        </Button>
      </div>
    </div>
  )
}

export default StatusBar
