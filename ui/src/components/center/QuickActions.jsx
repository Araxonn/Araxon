import React from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useWebSocket } from '../../hooks/useWebSocket'
import { Button } from '../ui/button'
import {
  Mic,
  MicOff,
  Eye,
  TerminalSquare,
  FolderOpen,
  Brain,
  Zap,
} from 'lucide-react'
import { cn } from '../../lib/utils'

const QuickActions = () => {
  const {
    activePanel,
    setActivePanel,
    micEnabled,
    toggleMic,
    setMemoryPanelOpen,
  } = useAppStore()

  const { sendCommand, sendMicToggle } = useWebSocket()

  const actions = [
    {
      id: 'mic',
      icon: micEnabled ? Mic : MicOff,
      label: 'Voice',
      tooltip: 'Toggle microphone',
      action: () => {
        toggleMic()
        sendMicToggle(!micEnabled)
      },
      isActive: false,
      disabled: false,
      color: micEnabled ? 'text-arx-cyan' : 'text-arx-red',
    },
    {
      id: 'vision',
      icon: Eye,
      label: 'Vision',
      tooltip: 'Analyze screen',
      action: () => {
        setActivePanel('orb')
        sendCommand('what do you see')
      },
      isActive: activePanel === 'orb',
      disabled: false,
      color: 'text-arx-cyan',
    },
    {
      id: 'terminal',
      icon: TerminalSquare,
      label: 'Terminal',
      tooltip: 'Open terminal',
      action: () => setActivePanel('terminal'),
      isActive: activePanel === 'terminal',
      disabled: false,
      color: 'text-arx-green',
    },
    {
      id: 'files',
      icon: FolderOpen,
      label: 'Files',
      tooltip: 'Browse files',
      action: () => setActivePanel('files'),
      isActive: activePanel === 'files',
      disabled: false,
      color: 'text-arx-orange',
    },
    {
      id: 'memory',
      icon: Brain,
      label: 'Memory',
      tooltip: 'View memory',
      action: () => {
        setActivePanel('memory')
        setMemoryPanelOpen(true)
        sendCommand('what do you remember')
      },
      isActive: activePanel === 'memory',
      disabled: false,
      color: 'text-arx-purple',
    },
    {
      id: 'automation',
      icon: Zap,
      label: 'Automation',
      tooltip: 'Automation status',
      action: () => setActivePanel('automation'),
      isActive: activePanel === 'automation',
      disabled: false,
      color: 'text-arx-blue',
    },
  ]

  return (
    <div className="flex justify-center gap-4 pt-4">
      {actions.map((action) => {
        const Icon = action.icon
        return (
          <Button
            key={action.id}
            variant="ghost"
            size="icon"
            className={cn(
              'h-14 w-14 rounded-full border-2 transition-all',
              action.isActive
                ? 'border-arx-blue bg-arx-active'
                : 'border-arx-border hover:border-arx-blue',
              action.color
            )}
            onClick={action.action}
            disabled={action.disabled}
            title={action.tooltip}
          >
            <Icon size={24} />
          </Button>
        )
      })}
    </div>
  )
}

export default QuickActions
