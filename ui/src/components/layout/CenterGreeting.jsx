import React from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useFullscreen, useMinimize } from '../../hooks/useFullscreen'
import { Button } from '../ui/button'
import {
  Maximize2,
  Minimize2,
  Square,
  Settings,
  Volume2,
  VolumeX,
} from 'lucide-react'
import { useWebSocket } from '../../hooks/useWebSocket'

const CenterGreeting = () => {
  const {
    araxonState,
    voiceEnabled,
    toggleVoice,
    setSettingsOpen,
  } = useAppStore()

  const { sendVoiceToggle } = useWebSocket()
  const { toggleFullscreenMode, isFullscreen: isFull } = useFullscreen()
  const { minimize } = useMinimize()

  const getTitle = () => {
    switch (araxonState) {
      case 'executing':
        return 'Executing Command'
      case 'code':
        return 'Code Assistant'
      case 'thinking':
        return 'Thinking...'
      default:
        return 'Hello, User'
    }
  }

  const getSubtitle = () => {
    switch (araxonState) {
      case 'executing':
        return 'Araxon is working on your request...'
      case 'code':
        return 'Ready to analyze and edit your code.'
      case 'thinking':
        return 'Processing your request...'
      default:
        return "I'm listening. How can I assist you today?"
    }
  }

  const handleMuteClick = () => {
    const next = !voiceEnabled
    toggleVoice()
    sendVoiceToggle(next)
  }

  return (
    <div className="flex items-start justify-between px-6 pt-5 pb-2">
      <div>
        <h1 className="text-2xl font-bold">
          <span className="text-arx-blue-bright">{getTitle()}</span>
        </h1>
        <p className="text-sm text-arx-secondary mt-1">{getSubtitle()}</p>
      </div>

      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-arx-muted hover:text-arx-text"
          onClick={toggleFullscreenMode}
          title={isFull ? 'Exit Fullscreen' : 'Enter Fullscreen'}
        >
          {isFull ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-arx-muted hover:text-arx-text"
          onClick={minimize}
          title="Minimize"
        >
          <Square size={16} />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-arx-muted hover:text-arx-text"
          onClick={() => setSettingsOpen(true)}
          title="Settings"
        >
          <Settings size={16} />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className={`h-8 w-8 ${!voiceEnabled ? 'text-arx-red' : 'text-arx-muted hover:text-arx-text'}`}
          onClick={handleMuteClick}
          title={!voiceEnabled ? 'Unmute' : 'Mute'}
        >
          {!voiceEnabled ? <VolumeX size={16} /> : <Volume2 size={16} />}
        </Button>
      </div>
    </div>
  )
}

export default CenterGreeting
