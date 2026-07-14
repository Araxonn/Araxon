import React, { useEffect } from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useWebSocket } from '../../hooks/useWebSocket'
import { ScrollArea } from '../ui/scroll-area'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Send, Trash2 } from 'lucide-react'

const TerminalPanel = () => {
  const { logsOutput, clearLogs } = useAppStore()
  const { sendCommand, sendNavChange } = useWebSocket()
  const [input, setInput] = React.useState('')

  useEffect(() => {
    sendNavChange('Terminal')
  }, [sendNavChange])

  const handleRunCommand = () => {
    if (input.trim()) {
      sendCommand(`run ${input}`)
      setInput('')
    }
  }

  const getLogColor = (level) => {
    switch (level?.toUpperCase()) {
      case 'ERROR':
        return 'text-arx-red'
      case 'WARNING':
        return 'text-arx-orange'
      case 'SUCCESS':
        return 'text-arx-green'
      default:
        return 'text-arx-secondary'
    }
  }

  return (
    <div className="flex flex-col h-full bg-arx-bg border-l border-arx-border">
      <div className="px-4 py-3 border-b border-arx-border">
        <h2 className="text-[11px] font-bold text-arx-text tracking-widest">TERMINAL</h2>
      </div>

      <div className="flex-1 min-h-0 overflow-hidden">
        <ScrollArea className="h-full w-full">
          <div className="p-4 font-mono text-xs space-y-1 whitespace-pre-wrap break-words">
            {logsOutput.length === 0 ? (
              <div className="text-arx-muted">Terminal ready...</div>
            ) : (
              logsOutput.slice(-50).map((log, idx) => (
                <div key={idx} className={getLogColor(log.level)}>
                  {log.timestamp && (
                    <span className="text-arx-muted mr-2">[{log.timestamp}]</span>
                  )}
                  {log.module && (
                    <span className="text-arx-blue mr-2">{log.module}</span>
                  )}
                  {typeof log === 'string' ? log : log.message}
                </div>
              ))
            )}
          </div>
        </ScrollArea>
      </div>

      <div className="border-t border-arx-border p-3 space-y-2">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleRunCommand()
            }}
            placeholder="Enter command..."
            className="h-7 text-xs bg-arx-input border-arx-border"
          />
          <Button
            size="sm"
            className="px-2 h-7"
            onClick={handleRunCommand}
            disabled={!input.trim()}
          >
            <Send size={12} />
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="px-2 h-7 border-arx-border"
            onClick={clearLogs}
          >
            <Trash2 size={12} />
          </Button>
        </div>
      </div>
    </div>
  )
}

export default TerminalPanel
