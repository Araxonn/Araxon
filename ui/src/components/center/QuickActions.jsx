import React from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useWebSocket } from '../../hooks/useWebSocket'
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
      action: () => {
        const next = !micEnabled
        toggleMic()
        sendMicToggle(next)
      },
      isActive: false,
      color: micEnabled ? 'text-arx-cyan' : 'text-arx-red',
    },
    {
      id: 'vision',
      icon: Eye,
      label: 'Vision',
      action: () => {
        setActivePanel('orb')
        sendCommand('what do you see')
      },
      isActive: activePanel === 'orb',
      color: 'text-arx-cyan',
    },
    {
      id: 'terminal',
      icon: TerminalSquare,
      label: 'Terminal',
      action: () => setActivePanel('terminal'),
      isActive: activePanel === 'terminal',
      color: 'text-arx-green',
    },
    {
      id: 'files',
      icon: FolderOpen,
      label: 'Files',
      action: () => setActivePanel('files'),
      isActive: activePanel === 'files',
      color: 'text-arx-orange',
    },
    {
      id: 'memory',
      icon: Brain,
      label: 'Memory',
      action: () => {
        setActivePanel('memory')
        setMemoryPanelOpen(true)
        sendCommand('what do you remember')
      },
      isActive: activePanel === 'memory',
      color: 'text-arx-purple',
    },
    {
      id: 'automation',
      icon: Zap,
      label: 'Automation',
      action: () => setActivePanel('automation'),
      isActive: activePanel === 'automation',
      color: 'text-arx-blue',
    },
  ]

  return (
    <div className="flex justify-center gap-6 px-4 py-3">
      {actions.map((action) => {
        const Icon = action.icon
        return (
          <button
            key={action.id}
            type="button"
            className="flex flex-col items-center gap-1.5 group"
            onClick={action.action}
          >
            <div
              className={cn(
                'h-12 w-12 rounded-full border flex items-center justify-center transition-all duration-200',
                action.isActive
                  ? 'border-arx-blue bg-arx-active shadow-arx-glow-sm'
                  : 'border-arx-border bg-arx-card/50 hover:border-arx-blue/50 hover:shadow-arx-glow-sm',
                action.color
              )}
            >
              <Icon size={20} />
            </div>
            <span className="text-[10px] text-arx-muted group-hover:text-arx-secondary transition-colors">
              {action.label}
            </span>
          </button>
        )
      })}
    </div>
  )
}

export default QuickActions
