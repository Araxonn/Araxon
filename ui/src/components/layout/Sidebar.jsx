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
  Puzzle,
  Settings,
  Plus,
  Smartphone,
  Wifi,
  PanelLeftClose,
} from 'lucide-react'
import { Button } from '../ui/button'
import { ScrollArea } from '../ui/scroll-area'
import ArxonLogo from '../ui/ArxonLogo'

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
    connected,
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
      action: () => setActiveNav('Plugins'),
    },
    {
      id: 'Settings',
      label: 'Settings',
      icon: Settings,
      action: () => setSettingsOpen(true),
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
      useAppStore.setState({ araxonState: 'code', activePanel: 'orb' })
    } else if (mode === 'Execute Mode') {
      useAppStore.setState({ araxonState: 'executing' })
      setActivePanel('orb')
    } else if (mode === 'Assist Mode') {
      useAppStore.setState({ araxonState: 'listening' })
      setActivePanel('orb')
    } else {
      setActivePanel('orb')
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
    <div className="w-56 bg-arx-sidebar border-r border-arx-border flex flex-col h-full shrink-0">
      <div className="px-4 py-4 flex items-center justify-between border-b border-arx-border">
        <div className="flex items-center gap-2.5">
          <ArxonLogo size="md" />
          <span className="text-sm font-bold text-arx-text tracking-wide">
            ARAXON <span className="text-arx-blue">Ai</span>
          </span>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7 text-arx-muted hover:text-arx-text"
        >
          <PanelLeftClose size={14} />
        </Button>
      </div>

      <ScrollArea className="flex-1">
        <div className="px-3 py-3 border-b border-arx-border">
          <div className="text-[10px] font-semibold text-arx-muted uppercase tracking-widest mb-2 px-2">
            Workspace
          </div>
          <div className="space-y-0.5">
            {workspaceItems.map((item) => {
              const Icon = item.icon
              const isActive = activeNav === item.id
              return (
                <Button
                  key={item.id}
                  variant="ghost"
                  className={cn(
                    'w-full justify-start text-sm h-8 rounded-md border-l-2 border-transparent',
                    isActive
                      ? 'arx-nav-active'
                      : 'text-arx-muted hover:text-arx-text hover:bg-arx-active/50'
                  )}
                  onClick={item.action}
                >
                  <Icon size={15} className="mr-2.5 opacity-80" />
                  {item.label}
                </Button>
              )
            })}
          </div>
        </div>

        <div className="px-3 py-3 border-b border-arx-border">
          <div className="text-[10px] font-semibold text-arx-muted uppercase tracking-widest mb-2 px-2">
            Modes
          </div>
          <div className="space-y-1">
            {modes.map((mode) => {
              const isActive = activeMode === mode
              return (
                <Button
                  key={mode}
                  variant="ghost"
                  className={cn(
                    'w-full justify-between text-xs h-8 px-3 rounded-lg',
                    isActive
                      ? 'arx-mode-active'
                      : 'text-arx-muted hover:text-arx-text hover:bg-arx-active/40'
                  )}
                  onClick={() => handleModeClick(mode)}
                >
                  <span>{mode}</span>
                  {isActive && (
                    <div className="w-1.5 h-1.5 bg-arx-blue rounded-full shadow-arx-glow-sm" />
                  )}
                </Button>
              )
            })}
          </div>
        </div>

        <div className="px-3 py-3 border-b border-arx-border">
          <div className="text-[10px] font-semibold text-arx-muted uppercase tracking-widest mb-2 px-2">
            Routines
          </div>
          <div className="space-y-0.5">
            {routines.map((routine) => (
              <Button
                key={routine.name}
                variant="ghost"
                className="w-full justify-start text-xs h-7 text-arx-muted hover:text-arx-text"
                onClick={() => handleRoutineClick(routine)}
              >
                <span className="mr-2">{routine.icon}</span>
                {routine.name}
              </Button>
            ))}
            <Button
              variant="ghost"
              className="w-full justify-start text-xs h-7 text-arx-blue hover:text-arx-cyan mt-1"
              onClick={() => useAppStore.setState({ createRoutineOpen: true })}
            >
              <Plus size={14} className="mr-2" />
              Create New Routine
            </Button>
          </div>
        </div>

        <div className="px-3 py-3">
          <div className="text-[10px] font-semibold text-arx-muted uppercase tracking-widest mb-2 px-2">
            Connect
          </div>
          <div className="space-y-0.5">
            <Button
              variant="ghost"
              className="w-full justify-start text-xs h-7 text-arx-muted hover:text-arx-text"
              onClick={() =>
                addNotification({
                  id: Math.random(),
                  type: 'info',
                  title: 'Mobile Link',
                  message: 'Feature coming soon',
                })
              }
            >
              <Smartphone size={14} className="mr-2" />
              Mobile Link
            </Button>
            <Button
              variant="ghost"
              className="w-full justify-between text-xs h-7 text-arx-secondary hover:text-arx-text"
            >
              <span className="flex items-center">
                <Wifi size={14} className="mr-2" />
                Araxon Core
              </span>
              <span className="text-[10px] text-arx-muted">v2.0.0</span>
            </Button>
          </div>
        </div>
      </ScrollArea>

      <div className="px-4 py-2.5 border-t border-arx-border">
        <div className="flex items-center gap-2 text-[10px] font-semibold tracking-wider">
          <div
            className={cn(
              'w-1.5 h-1.5 rounded-full',
              connected ? 'bg-arx-green shadow-[0_0_6px_#10B981]' : 'bg-arx-orange'
            )}
          />
          <span className={connected ? 'text-arx-green' : 'text-arx-orange'}>
            {connected ? 'ONLINE' : 'CONNECTING'}
          </span>
        </div>
      </div>
    </div>
  )
}

export default Sidebar
