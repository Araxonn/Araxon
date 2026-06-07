import React from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useWebSocket } from '../../hooks/useWebSocket'
import { cn } from '../../lib/utils'
import {
  LayoutDashboard,
  Users,
  Brain,
  Zap,
  Mic,
  Eye,
  Terminal,
  Files,
  Puzzle,
  Settings,
  Settings2,
  Eye as ObserveIcon,
  ArrowRight,
  Plus,
  Smartphone,
  Wifi,
} from 'lucide-react'
import { Button } from '../ui/button'

const Sidebar = () => {
  const {
    activeNav,
    setActiveNav,
    activeMode,
    setActiveMode,
    setActivePanel,
    setMemoryPanelOpen,
    setSettingsOpen,
    addNotification,
  } = useAppStore()

  const { sendCommand, sendNavChange } = useWebSocket()

  const workspaceItems = [
    {
      id: 'Dashboard',
      label: 'Dashboard',
      icon: LayoutDashboard,
      action: () => {
        setActiveNav('Dashboard')
        setActivePanel('orb')
      },
    },
    {
      id: 'Agents',
      label: 'Agents',
      icon: Users,
      action: () => {
        setActiveNav('Agents')
        sendNavChange('Agents')
      },
    },
    {
      id: 'Memory',
      label: 'Memory',
      icon: Brain,
      action: () => {
        setActiveNav('Memory')
        setActivePanel('memory')
        setMemoryPanelOpen(true)
        sendNavChange('Memory')
      },
    },
    {
      id: 'Automation',
      label: 'Automation',
      icon: Zap,
      action: () => {
        setActiveNav('Automation')
        setActivePanel('automation')
        sendNavChange('Automation')
      },
    },
    {
      id: 'Voice',
      label: 'Voice',
      icon: Mic,
      action: () => {
        setActiveNav('Voice')
        sendCommand('voice control')
      },
    },
    {
      id: 'Vision',
      label: 'Vision',
      icon: Eye,
      action: () => {
        setActiveNav('Vision')
        sendCommand('what do you see')
      },
    },
    {
      id: 'Terminal',
      label: 'Terminal',
      icon: Terminal,
      action: () => {
        setActiveNav('Terminal')
        setActivePanel('terminal')
      },
    },
    {
      id: 'Plugins',
      label: 'Plugins',
      icon: Puzzle,
      action: () => {
        setActiveNav('Plugins')
      },
    },
  ]

  const modes = [
    'Observe Mode',
    'Assist Mode',
    'Execute Mode',
    'Autonomous Mode',
    'Code Mode',
  ]

  const routines = [
    { name: 'Morning Routine', icon: '☀️', cmd: 'morning' },
    { name: 'Coding Setup', icon: '💻', cmd: 'coding' },
    { name: 'Study Mode', icon: '📚', cmd: 'study' },
    { name: 'Gaming Mode', icon: '🎮', cmd: 'gaming' },
  ]

  const handleModeClick = (mode) => {
    setActiveMode(mode)
    if (mode === 'Code Mode') {
      useAppStore.setState({ araxonState: 'code' })
      setActivePanel('code')
    }
    sendCommand(`${mode.toLowerCase()}`)
  }

  const handleRoutineClick = (routine) => {
    addNotification({
      id: Math.random(),
      type: 'info',
      title: 'Routine Started',
      message: `Launching ${routine.name}...`,
    })
    sendCommand(`launch ${routine.cmd} workspace`)
  }

  return (
    <div className="w-56 bg-arx-sidebar border-r border-arx-border flex flex-col h-screen overflow-y-auto">
      {/* Logo Row */}
      <div className="px-4 py-6 flex items-center justify-between border-b border-arx-border">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-arx-blue rounded-sm flex items-center justify-center text-white text-xs font-bold">
            △
          </div>
          <span className="text-sm font-bold text-arx-text">ARAXON Ai</span>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-arx-muted hover:text-arx-text"
          onClick={() => setSettingsOpen(true)}
        >
          <Settings size={18} />
        </Button>
      </div>

      {/* Workspace Navigation */}
      <div className="px-4 py-4 border-b border-arx-border">
        <div className="text-xs font-semibold text-arx-muted uppercase mb-3">
          Workspace
        </div>
        <div className="space-y-1">
          {workspaceItems.map((item) => {
            const Icon = item.icon
            const isActive = activeNav === item.id
            return (
              <Button
                key={item.id}
                variant="ghost"
                className={cn(
                  'w-full justify-start text-sm h-8',
                  isActive
                    ? 'bg-arx-active text-arx-blue'
                    : 'text-arx-muted hover:text-arx-text'
                )}
                onClick={item.action}
              >
                <Icon size={16} className="mr-3" />
                {item.label}
              </Button>
            )
          })}
        </div>
      </div>

      {/* Modes */}
      <div className="px-4 py-4 border-b border-arx-border">
        <div className="text-xs font-semibold text-arx-muted uppercase mb-3">
          Modes
        </div>
        <div className="space-y-1">
          {modes.map((mode) => (
            <Button
              key={mode}
              variant="ghost"
              className={cn(
                'w-full justify-between text-sm h-8 px-2',
                activeMode === mode
                  ? 'bg-arx-active text-arx-blue'
                  : 'text-arx-muted hover:text-arx-text'
              )}
              onClick={() => handleModeClick(mode)}
            >
              <span>{mode}</span>
              {activeMode === mode && (
                <div className="w-2 h-2 bg-arx-blue rounded-full" />
              )}
            </Button>
          ))}
        </div>
      </div>

      {/* Routines */}
      <div className="px-4 py-4 border-b border-arx-border">
        <div className="text-xs font-semibold text-arx-muted uppercase mb-3">
          Routines
        </div>
        <div className="space-y-1">
          {routines.map((routine) => (
            <Button
              key={routine.name}
              variant="ghost"
              className="w-full justify-start text-sm h-8 text-arx-muted hover:text-arx-text"
              onClick={() => handleRoutineClick(routine)}
            >
              <span className="mr-2 text-lg">{routine.icon}</span>
              {routine.name}
            </Button>
          ))}
          <Button
            variant="ghost"
            className="w-full justify-start text-sm h-8 text-arx-blue hover:text-arx-cyan mt-2"
            onClick={() => useAppStore.setState({ createRoutineOpen: true })}
          >
            <Plus size={16} className="mr-2" />
            Create New Routine
          </Button>
        </div>
      </div>

      {/* Connect */}
      <div className="px-4 py-4 mt-auto border-t border-arx-border">
        <div className="text-xs font-semibold text-arx-muted uppercase mb-3">
          Connect
        </div>
        <div className="space-y-2">
          <Button
            variant="ghost"
            className="w-full justify-start text-sm h-8 text-arx-muted hover:text-arx-text"
            onClick={() =>
              addNotification({
                id: Math.random(),
                type: 'info',
                title: 'Mobile Link',
                message: 'Feature coming soon',
              })
            }
          >
            <Smartphone size={16} className="mr-2" />
            Mobile Link
          </Button>
          <Button
            variant="ghost"
            className="w-full justify-start text-sm h-8 text-arx-green"
            onClick={() =>
              addNotification({
                id: Math.random(),
                type: 'success',
                title: 'Connected',
                message: 'Araxon Core v2.0.0 Online',
              })
            }
          >
            <Wifi size={16} className="mr-2" />
            Araxon Core
          </Button>
        </div>
      </div>

      {/* Status */}
      <div className="px-4 py-2 border-t border-arx-border text-xs text-arx-muted">
        <div className="flex items-center gap-2 text-arx-green">
          <div className="w-2 h-2 bg-arx-green rounded-full" />
          ONLINE
        </div>
      </div>
    </div>
  )
}

export default Sidebar
