import React, { useEffect } from 'react'
import { useAppStore } from './store/useAppStore'
import { useWebSocket } from './hooks/useWebSocket'
import Sidebar from './components/layout/Sidebar'
import CenterHeader from './components/layout/CenterHeader'
import StatusBar from './components/layout/StatusBar'
import NotificationStack from './components/layout/NotificationToast'
import CenterPanel from './components/center/CenterPanel'
import CommandStream from './components/stream/CommandStream'
import TerminalPanel from './components/panels/TerminalPanel'
import FilesPanel from './components/panels/FilesPanel'
import MemoryPanel from './components/panels/MemoryPanel'
import AutomationPanel from './components/panels/AutomationPanel'
import CodePanel from './components/panels/CodePanel'
import SettingsOverlay from './components/overlays/SettingsOverlay'
import CreateRoutineDialog from './components/overlays/CreateRoutineDialog'

const App = () => {
  const { activePanel, isFullscreen } = useAppStore()
  useWebSocket()

  useEffect(() => {
    // Initialize on mount
    console.log('ARAXON UI Initialized')
  }, [])

  const renderRightPanel = () => {
    switch (activePanel) {
      case 'terminal':
        return <TerminalPanel />
      case 'files':
        return <FilesPanel />
      case 'memory':
        return <MemoryPanel />
      case 'automation':
        return <AutomationPanel />
      case 'code':
        return <CodePanel />
      default:
        return <CommandStream />
    }
  }

  return (
    <div className={`flex flex-col h-screen w-screen bg-arx-bg text-arx-text ${isFullscreen ? 'fullscreen' : ''}`}>
      {/* Header */}
      <CenterHeader />

      {/* Main Content */}
      <div className="flex-1 flex min-h-0 overflow-hidden">
        {/* Sidebar */}
        <Sidebar />

        {/* Center Panel */}
        <CenterPanel />

        {/* Right Panel / Command Stream */}
        {renderRightPanel()}
      </div>

      {/* Status Bar */}
      <StatusBar />

      {/* Notifications */}
      <NotificationStack />

      {/* Overlays */}
      <SettingsOverlay />
      <CreateRoutineDialog />
    </div>
  )
}

export default App