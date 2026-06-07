import React from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useWebSocket } from '../../hooks/useWebSocket'
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

const CenterHeader = () => {
  const {
    araxonState,
    isMuted,
    isFullscreen,
    toggleMute,
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

  const handleMuteClick = () => {
    toggleMute()
    sendVoiceToggle(!isMuted)
  }

  return (
    <div className="flex items-center justify-between px-6 py-4 border-b border-arx-border bg-arx-bg">
      <h1 className="text-xl font-bold text-arx-text">{getTitle()}</h1>

      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          className="h-10 w-10 text-arx-muted hover:text-arx-text"
          onClick={toggleFullscreenMode}
          title={isFull ? 'Exit Fullscreen' : 'Enter Fullscreen'}
        >
          {isFull ? (
            <Minimize2 size={20} />
          ) : (
            <Maximize2 size={20} />
          )}
        </Button>

        <Button
          variant="ghost"
          size="icon"
          className="h-10 w-10 text-arx-muted hover:text-arx-text"
          onClick={minimize}
          title="Minimize"
        >
          <Square size={20} />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          className="h-10 w-10 text-arx-muted hover:text-arx-text"
          onClick={() => setSettingsOpen(true)}
          title="Settings"
        >
          <Settings size={20} />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          className={`h-10 w-10 ${
            isMuted
              ? 'text-arx-red'
              : 'text-arx-muted hover:text-arx-text'
          }`}
          onClick={handleMuteClick}
          title={isMuted ? 'Unmute' : 'Mute'}
        >
          {isMuted ? (
            <VolumeX size={20} />
          ) : (
            <Volume2 size={20} />
          )}
        </Button>
      </div>
    </div>
  )
}

export default CenterHeader
