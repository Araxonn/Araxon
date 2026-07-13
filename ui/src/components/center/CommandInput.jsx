import React, { useRef, useState } from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useWebSocket } from '../../hooks/useWebSocket'
import { Button } from '../ui/button'
import { Paperclip, Mic, ArrowRight, Loader2 } from 'lucide-react'
import { cn } from '../../lib/utils'

const CommandInput = () => {
  const {
    araxonState,
    activeMode,
    micEnabled,
    toggleMic,
    addNotification,
  } = useAppStore()

  const { sendCommand, sendFileIngest, sendMicToggle, sendInterrupt } =
    useWebSocket()

  const [input, setInput] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const fileInputRef = useRef(null)

  const handleSendCommand = () => {
    if (input.trim()) {
      setIsProcessing(true)
      sendCommand(input)
      setInput('')
      setTimeout(() => setIsProcessing(false), 500)
    }
  }

  const handleFileIngest = async (e) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        const content = event.target?.result
        sendFileIngest(content, file.name)
        addNotification({
          id: Math.random(),
          type: 'info',
          title: 'File Ingestion',
          message: `Ingesting ${file.name}...`,
        })
      }
      reader.readAsText(file)
    }
  }

  const handleMicToggle = () => {
    const next = !micEnabled
    toggleMic()
    sendMicToggle(next)
  }

  const getQuickChips = () => {
    if (activeMode === 'Execute Mode') {
      return ['Open VS Code', 'Show Logs', 'Run Diagnostics', 'Task Manager', 'Stop Execution']
    }
    if (activeMode === 'Code Mode') {
      return [
        'Explain Code',
        'Optimize Code',
        'Find Bugs',
        'Generate Tests',
        'Refactor',
        'Docs',
        'Commit Changes',
      ]
    }
    return [
      'Open VS Code',
      'Summarize Notes',
      'Show System Status',
      'Run Morning Routine',
      'Search Files',
    ]
  }

  const handleQuickChip = (chip) => {
    if (chip === 'Stop Execution') {
      sendInterrupt()
    } else if (chip === 'Show Logs') {
      useAppStore.setState({ activeTab: 'Logs' })
    } else {
      sendCommand(chip)
    }
  }

  const getPlaceholder = () => {
    if (araxonState === 'executing') {
      return 'Type to interrupt or give new command...'
    }
    if (araxonState === 'code') {
      return 'Ask about the code or request changes...'
    }
    return 'Ask Araxon anything or give a command...'
  }

  return (
    <div className="px-4 py-4 border-t border-arx-border/60 space-y-3">
      <div className="relative flex items-center gap-2 arx-input-field px-3 py-2.5">
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.md,.py,.pdf,.json,.jsx,.tsx,.js,.ts"
          onChange={handleFileIngest}
          className="hidden"
        />

        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7 text-arx-muted hover:text-arx-text shrink-0"
          onClick={() => fileInputRef.current?.click()}
          title="Attach file"
        >
          <Paperclip size={16} />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          className={cn(
            'h-7 w-7 shrink-0',
            micEnabled ? 'text-arx-cyan' : 'text-arx-red'
          )}
          onClick={handleMicToggle}
          title={micEnabled ? 'Disable mic' : 'Enable mic'}
        >
          <Mic size={16} />
        </Button>

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !isProcessing) handleSendCommand()
          }}
          placeholder={getPlaceholder()}
          className="flex-1 bg-transparent text-sm text-arx-text placeholder:text-arx-muted focus:outline-none min-w-0"
        />

        <Button
          size="sm"
          className="h-8 px-4 bg-arx-blue hover:bg-arx-blue/90 text-white rounded-lg gap-1.5 shrink-0"
          onClick={handleSendCommand}
          disabled={!input.trim() || isProcessing}
        >
          {isProcessing ? (
            <Loader2 size={14} className="animate-spin" />
          ) : (
            <>
              Send
              <ArrowRight size={14} />
            </>
          )}
        </Button>
      </div>

      <div className="flex flex-wrap gap-2">
        {getQuickChips().map((chip) => (
          <button
            key={chip}
            type="button"
            className={cn(
              'arx-chip',
              chip === 'Stop Execution' && 'border-arx-red/40 text-arx-red hover:border-arx-red'
            )}
            onClick={() => handleQuickChip(chip)}
          >
            {chip}
          </button>
        ))}
      </div>
    </div>
  )
}

export default CommandInput
