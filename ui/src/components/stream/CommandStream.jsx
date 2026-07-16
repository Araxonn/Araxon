import React from 'react'
import { useAppStore } from '../../store/useAppStore'
import { motion } from 'framer-motion'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu'
import { Button } from '../ui/button'
import { MoreHorizontal, Maximize2 } from 'lucide-react'
import StreamTabs from './StreamTabs'
import VoiceWaveform from '../orb/VoiceWaveform'

const CommandStream = () => {
  const {
    commandStreamExpanded,
    toggleCommandStream,
    clearTranscript,
    transcript,
    araxonState,
  } = useAppStore()

  const handleExportLogs = () => {
    const text = transcript
      .map((entry) => `${entry.role.toUpperCase()}: ${entry.text}`)
      .join('\n\n')
    const element = document.createElement('a')
    element.setAttribute(
      'href',
      `data:text/plain;charset=utf-8,${encodeURIComponent(text)}`
    )
    element.setAttribute('download', `araxon-logs-${Date.now()}.txt`)
    element.style.display = 'none'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  const handleCopyAll = () => {
    const text = transcript
      .map((entry) => `${entry.role.toUpperCase()}: ${entry.text}`)
      .join('\n\n')
    navigator.clipboard.writeText(text)
  }

  const getFooterLabel = () => {
    switch (araxonState) {
      case 'executing':
        return 'Araxon is executing...'
      case 'code':
        return 'Code mode active'
      case 'thinking':
        return 'Araxon is thinking...'
      default:
        return 'Araxon is listening...'
    }
  }

  return (
    <motion.div
      layout
      className={`flex flex-col border-l border-arx-border bg-arx-sidebar/50 shrink-0 ${
        commandStreamExpanded ? 'w-96' : 'w-80'
      }`}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
    >
      <div className="flex items-center justify-between px-4 py-3 border-b border-arx-border">
        <h2 className="text-[11px] font-bold text-arx-text tracking-widest">
          COMMAND STREAM
        </h2>

        <div className="flex items-center gap-1">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 text-arx-muted hover:text-arx-text"
              >
                <MoreHorizontal size={14} />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-40 text-xs">
              <DropdownMenuItem onClick={clearTranscript}>
                Clear Stream
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleExportLogs}>
                Export Logs
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleCopyAll}>
                Copy All
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6 text-arx-muted hover:text-arx-text"
            onClick={toggleCommandStream}
          >
            <Maximize2 size={14} />
          </Button>
        </div>
      </div>

      <div className="flex-1 min-h-0 overflow-hidden flex flex-col">
        <StreamTabs />
      </div>

      <div className="px-4 py-2 border-t border-arx-border flex items-center gap-2">
        <div className="w-16 h-4 overflow-hidden opacity-50">
          <VoiceWaveform compact />
        </div>
        <span className="text-[10px] text-arx-muted">{getFooterLabel()}</span>
      </div>
    </motion.div>
  )
}

export default CommandStream
