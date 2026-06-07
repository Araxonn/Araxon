import React, { useRef, useState } from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useWebSocket } from '../../hooks/useWebSocket'
import { Button } from '../ui/button'
import { Paperclip, Mic, Send, Loader2 } from 'lucide-react'

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
    toggleMic()
    sendMicToggle(!micEnabled)
  }

  const getQuickChips = () => {
    if (activeMode === 'Execute Mode') {
      return [
        'Show Logs',
        'Run Diagnostics',
        'Task Manager',
        'Stop Execution',
      ]
    }
    if (activeMode === 'Code Mode') {
      return [
        'Explain Code',
        'Optimize Code',
        'Find Bugs',
        'Generate Tests',
        'Refactor',
        'Docs',
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
    <div className="space-y-2 px-4 py-4 border-t border-arx-border">
      {/* Quick Chips */}
      <div className="flex flex-wrap gap-2 mb-3">
        {getQuickChips().map((chip) => (
          <Button
            key={chip}
            variant="outline"
            size="sm"
            className="text-xs h-6 text-arx-secondary hover:text-arx-text"
            onClick={() => handleQuickChip(chip)}
          >
            {chip === 'Stop Execution' ? (
              <span className="text-arx-red font-bold">{chip}</span>
            ) : (
              chip
            )}
          </Button>
        ))}
      </div>

      {/* Input Row */}
      <div className="flex items-center gap-2">
        {/* File Input */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.md,.py,.pdf,.json"
          onChange={handleFileIngest}
          className="hidden"
        />

        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-arx-muted hover:text-arx-text"
          onClick={() => fileInputRef.current?.click()}
          title="Attach file"
        >
          <Paperclip size={16} />
        </Button>

        {/* Mic Button */}
        <Button
          variant="ghost"
          size="icon"
          className={`h-8 w-8 ${
            micEnabled
              ? 'text-arx-cyan'
              : 'text-arx-red'
          }`}
          onClick={handleMicToggle}
          title={micEnabled ? 'Disable mic' : 'Enable mic'}
        >
          <Mic size={16} />
        </Button>

        {/* Text Input */}
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !isProcessing) {
              handleSendCommand()
            }
          }}
          placeholder={getPlaceholder()}
          className="flex-1 h-8 px-3 bg-arx-input border border-arx-border rounded text-sm text-arx-text placeholder-arx-muted focus:outline-none focus:border-arx-blue transition-colors"
        />

        {/* Send Button */}
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-arx-blue hover:text-arx-cyan disabled:opacity-50"
          onClick={handleSendCommand}
          disabled={!input.trim() || isProcessing}
          title="Send command"
        >
          {isProcessing ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Send size={16} />
          )}
        </Button>
      </div>
    </div>
  )
}

export default CommandInput
