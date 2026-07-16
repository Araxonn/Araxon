import React from 'react'
import { motion } from 'framer-motion'
import { Copy, CheckCircle2 } from 'lucide-react'
import { Button } from '../ui/button'
import { Progress } from '../ui/progress'
import ArxonLogo from '../ui/ArxonLogo'

const TranscriptEntry = ({ entry, onCopy }) => {
  const isUser = entry.role === 'user'
  const timestamp =
    entry.timestamp ||
    new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

  const renderContent = () => {
    if (entry.type === 'checklist' && entry.items) {
      return (
        <ul className="space-y-1 text-xs">
          {entry.items.map((item, i) => (
            <li key={i} className="flex items-center gap-2">
              {item.status === 'done' ? (
                <CheckCircle2 size={12} className="text-arx-green shrink-0" />
              ) : (
                <span className="w-3 h-3 rounded-full border border-arx-muted shrink-0" />
              )}
              <span className={item.status === 'done' ? 'text-arx-secondary' : 'text-arx-muted'}>
                {item.text}
                {item.status === 'done' && (
                  <span className="text-arx-green ml-1">Done</span>
                )}
                {item.status === 'pending' && (
                  <span className="text-arx-orange ml-1">Pending</span>
                )}
              </span>
            </li>
          ))}
        </ul>
      )
    }

    if (entry.type === 'progress') {
      return (
        <div className="space-y-2">
          <p className="text-xs text-arx-secondary">{entry.text}</p>
          <Progress value={entry.percent || 0} className="h-1.5" />
          <span className="text-[10px] text-arx-cyan">{entry.percent || 0}%</span>
        </div>
      )
    }

    if (entry.type === 'code') {
      return (
        <pre className="text-[11px] font-mono text-arx-cyan bg-arx-input/80 p-2 rounded border border-arx-border overflow-x-auto">
          {entry.text}
        </pre>
      )
    }

    return (
      <p className="text-xs text-arx-secondary whitespace-pre-wrap break-words leading-relaxed">
        {entry.text}
      </p>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-4 group"
    >
      <div className="flex items-center gap-2 mb-1.5">
        {isUser ? (
          <div className="w-5 h-5 rounded-full bg-arx-blue/20 flex items-center justify-center text-[10px]">
            👤
          </div>
        ) : (
          <ArxonLogo size="sm" className="!w-5 !h-5 !text-[8px]" />
        )}
        <span className="text-[10px] font-semibold text-arx-text">
          {isUser ? 'You' : 'Araxon Ai'}
        </span>
        <span className="text-[10px] text-arx-muted ml-auto">{timestamp}</span>
      </div>

      <div
        className={`relative ml-7 p-3 rounded-lg border ${
          isUser
            ? 'bg-arx-active/60 border-arx-border'
            : 'bg-arx-card/80 border-arx-border/60'
        }`}
      >
        {renderContent()}

        <Button
          variant="ghost"
          size="icon"
          className="h-5 w-5 absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity text-arx-muted"
          onClick={() => onCopy(entry.text)}
        >
          <Copy size={11} />
        </Button>
      </div>
    </motion.div>
  )
}

export default TranscriptEntry
