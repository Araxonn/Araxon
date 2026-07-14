import React from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useWebSocket } from '../../hooks/useWebSocket'
import { ScrollArea } from '../ui/scroll-area'
import { Button } from '../ui/button'
import { Copy, ExternalLink } from 'lucide-react'

const CodePanel = ({ embedded = false }) => {
  const { codeFile, codeSuggestions } = useAppStore()
  const { sendCommand } = useWebSocket()

  const handleCopyCode = () => {
    navigator.clipboard.writeText(codeFile.content)
  }

  const handleOpenInEditor = () => {
    sendCommand(`open ${codeFile.name}`)
  }

  const handleApplySuggestion = (title) => {
    sendCommand(`apply ${title}`)
  }

  const handleApplyAll = () => {
    sendCommand('apply all code suggestions')
  }

  const highlightLine = (line) => {
    if (!line) return <span>&nbsp;</span>
    const parts = []
    const keywords = /\b(import|export|default|function|const|return|from|useState)\b/g
    let last = 0
    let match
    while ((match = keywords.exec(line)) !== null) {
      if (match.index > last) {
        parts.push(<span key={last}>{line.slice(last, match.index)}</span>)
      }
      parts.push(
        <span key={match.index} className="text-arx-purple">
          {match[0]}
        </span>
      )
      last = match.index + match[0].length
    }
    if (last < line.length) {
      parts.push(<span key={last}>{line.slice(last)}</span>)
    }
    return parts.length ? parts : line
  }

  return (
    <div className={`flex ${embedded ? 'h-full' : 'gap-3 h-full'}`}>
      <div className="flex-1 flex flex-col min-w-0">
        <div className="px-4 py-2 border-b border-arx-border flex items-center justify-between bg-arx-sidebar/50">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-semibold text-arx-muted uppercase tracking-wider">
              Active File
            </span>
            <span className="text-xs font-semibold text-arx-cyan truncate">
              {codeFile.name || 'No file selected'}
            </span>
          </div>
          <div className="flex gap-1">
            <Button
              size="icon"
              variant="ghost"
              className="h-6 w-6 text-arx-muted hover:text-arx-text"
              onClick={handleCopyCode}
              disabled={!codeFile.content}
            >
              <Copy size={12} />
            </Button>
            <Button
              size="icon"
              variant="ghost"
              className="h-6 w-6 text-arx-muted hover:text-arx-text"
              onClick={handleOpenInEditor}
              disabled={!codeFile.name}
            >
              <ExternalLink size={12} />
            </Button>
          </div>
        </div>

        <ScrollArea className="flex-1 w-full">
          <div className="p-4 font-mono text-xs text-arx-secondary whitespace-pre-wrap break-words">
            {codeFile.content ? (
              <div>
                {codeFile.content.split('\n').map((line, idx) => (
                  <div key={idx} className="flex gap-3 leading-5 hover:bg-arx-active/30">
                    <span className="text-arx-muted w-6 text-right select-none shrink-0">
                      {idx + 1}
                    </span>
                    <span className="flex-1">{highlightLine(line)}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-arx-muted text-center py-8">
                No code file loaded
              </div>
            )}
          </div>
        </ScrollArea>
      </div>

      <div className="w-56 flex flex-col border-l border-arx-border bg-arx-sidebar/30">
        <div className="px-3 py-2 border-b border-arx-border text-[10px] font-semibold text-arx-muted uppercase tracking-wider">
          Suggestions
        </div>

        <ScrollArea className="flex-1 w-full p-3">
          {codeSuggestions.length === 0 ? (
            <div className="text-center text-arx-muted text-xs py-4">
              No suggestions
            </div>
          ) : (
            <div className="space-y-2">
              {codeSuggestions.map((suggestion, idx) => (
                <div
                  key={idx}
                  className="p-2.5 arx-glass rounded-lg space-y-2"
                >
                  <div>
                    <div className="text-xs font-semibold text-arx-text">
                      {suggestion.title}
                    </div>
                    <div className="text-[11px] text-arx-muted mt-0.5">
                      {suggestion.description}
                    </div>
                  </div>
                  <Button
                    size="sm"
                    className="w-full h-6 text-xs bg-arx-blue/20 text-arx-blue hover:bg-arx-blue/30 border border-arx-blue/30"
                    onClick={() => handleApplySuggestion(suggestion.title)}
                  >
                    Apply
                  </Button>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>

        {codeSuggestions.length > 0 && (
          <div className="border-t border-arx-border p-2">
            <Button
              size="sm"
              className="w-full h-7 text-xs bg-arx-blue text-white hover:bg-arx-blue/90"
              onClick={handleApplyAll}
            >
              Apply All
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}

export default CodePanel
