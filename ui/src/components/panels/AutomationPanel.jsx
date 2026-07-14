import React, { useEffect } from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useWebSocket } from '../../hooks/useWebSocket'
import { ScrollArea } from '../ui/scroll-area'
import { Button } from '../ui/button'
import { Play, X } from 'lucide-react'

const AutomationPanel = () => {
  const { automationProcesses } = useAppStore()
  const { sendCommand, sendNavChange } = useWebSocket()

  useEffect(() => {
    sendNavChange('Automation')
    const interval = setInterval(() => sendNavChange('Automation'), 10000)
    return () => clearInterval(interval)
  }, [sendNavChange])

  const workspaceProfiles = [
    { name: 'mern', label: 'MERN', icon: '🔴' },
    { name: 'python', label: 'Python', icon: '🐍' },
    { name: 'ai', label: 'AI', icon: '🤖' },
    { name: 'focus', label: 'Focus', icon: '🎯' },
  ]

  const handleLaunchProfile = (profile) => {
    sendCommand(`launch ${profile} workspace`)
  }

  const handleKillProcess = (processName) => {
    sendCommand(`close ${processName}`)
  }

  return (
    <div className="flex flex-col h-full bg-arx-bg border-l border-arx-border">
      <div className="px-4 py-3 border-b border-arx-border">
        <h2 className="text-[11px] font-bold text-arx-text tracking-widest">AUTOMATION</h2>
      </div>

      <div className="border-b border-arx-border p-3 space-y-3">
        <div className="text-xs font-semibold text-arx-muted uppercase">Workspace</div>
        <div className="grid grid-cols-2 gap-2">
          {workspaceProfiles.map((profile) => (
            <Button
              key={profile.name}
              variant="outline"
              size="sm"
              className="h-8 text-xs border-arx-border"
              onClick={() => handleLaunchProfile(profile.name)}
            >
              <span className="mr-1">{profile.icon}</span>
              {profile.label}
            </Button>
          ))}
        </div>
      </div>

      <div className="flex-1 min-h-0 overflow-hidden flex flex-col">
        <div className="px-3 pt-3 text-xs font-semibold text-arx-muted uppercase">
          Active Processes
        </div>
        <ScrollArea className="flex-1 w-full">
          <div className="p-3 space-y-2">
            {automationProcesses.length === 0 ? (
              <div className="text-center text-arx-muted text-sm py-8">
                No active processes detected
              </div>
            ) : (
              automationProcesses.map((proc, idx) => (
                <div
                  key={idx}
                  className="p-2 bg-arx-card rounded border border-arx-border flex items-center justify-between group"
                >
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-semibold text-arx-text truncate">
                      {proc.name}
                    </div>
                    <div className="text-xs text-arx-muted">
                      PID: {proc.pid} • CPU: {proc.cpu}% • MEM: {proc.memory}%
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 text-arx-red opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={() => handleKillProcess(proc.name)}
                  >
                    <X size={12} />
                  </Button>
                </div>
              ))
            )}
          </div>
        </ScrollArea>
      </div>
    </div>
  )
}

export default AutomationPanel
