import React, { useState } from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useWebSocket } from '../../hooks/useWebSocket'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/tabs'
import { ScrollArea } from '../ui/scroll-area'
import { Input } from '../ui/input'
import { Button } from '../ui/button'
import { Trash2 } from 'lucide-react'
import TranscriptEntry from './TranscriptEntry'
import AgentSteps from './AgentSteps'
import { cn } from '../../lib/utils'

const StreamTabs = () => {
  const {
    activeTab,
    setActiveTab,
    transcript,
    agentSteps,
    logsOutput,
    memoryStats,
    clearTranscript,
    clearLogs,
  } = useAppStore()

  const { sendCommand } = useWebSocket()
  const [memoryQuery, setMemoryQuery] = useState('')
  const [logsFilter, setLogsFilter] = useState('All')

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text)
  }

  const filteredLogs = logsOutput.filter((log) => {
    if (logsFilter === 'All') return true
    return log.level?.toUpperCase() === logsFilter.toUpperCase()
  })

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
    <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col min-h-0">
      <TabsList className="w-full justify-start rounded-none border-b border-arx-border bg-transparent h-9 px-3 gap-1">
        {['Commands', 'Sequences', 'Logs', 'Memory'].map((tab) => (
          <TabsTrigger
            key={tab}
            value={tab}
            className={cn(
              'text-[11px] h-7 px-3 rounded-full border border-transparent',
              'data-[state=active]:bg-arx-active data-[state=active]:text-arx-blue data-[state=active]:border-arx-border-glow'
            )}
          >
            {tab}
          </TabsTrigger>
        ))}
      </TabsList>

      <TabsContent value="Commands" className="flex-1 flex flex-col min-h-0 mt-0 data-[state=inactive]:hidden">
        <ScrollArea className="flex-1 px-3 py-3">
          {transcript.length === 0 ? (
            <div className="text-center text-arx-muted text-xs py-12">
              No commands yet
            </div>
          ) : (
            <div>
              {transcript.map((entry, idx) => (
                <TranscriptEntry key={idx} entry={entry} onCopy={handleCopy} />
              ))}
            </div>
          )}
        </ScrollArea>
        <div className="border-t border-arx-border p-2">
          <Button
            variant="outline"
            size="sm"
            className="w-full text-xs h-7 border-arx-border text-arx-muted hover:text-arx-text"
            onClick={clearTranscript}
          >
            <Trash2 size={12} className="mr-1" />
            Clear
          </Button>
        </div>
      </TabsContent>

      <TabsContent value="Sequences" className="flex-1 flex flex-col min-h-0 mt-0 data-[state=inactive]:hidden">
        <ScrollArea className="flex-1 p-3">
          {agentSteps.length === 0 ? (
            <div className="text-center text-arx-muted text-xs py-12">
              No sequences running
            </div>
          ) : (
            <AgentSteps steps={agentSteps} />
          )}
        </ScrollArea>
      </TabsContent>

      <TabsContent value="Logs" className="flex-1 flex flex-col min-h-0 mt-0 data-[state=inactive]:hidden">
        <div className="border-b border-arx-border p-2 flex gap-2">
          <select
            value={logsFilter}
            onChange={(e) => setLogsFilter(e.target.value)}
            className="text-xs bg-arx-input border border-arx-border rounded px-2 py-1 text-arx-text"
          >
            <option>All</option>
            <option>INFO</option>
            <option>WARNING</option>
            <option>ERROR</option>
            <option>SUCCESS</option>
          </select>
          <Button
            variant="outline"
            size="sm"
            className="text-xs ml-auto h-7 border-arx-border"
            onClick={clearLogs}
          >
            Clear
          </Button>
        </div>
        <ScrollArea className="flex-1 p-3 font-mono text-xs">
          {filteredLogs.length === 0 ? (
            <div className="text-arx-muted">No logs</div>
          ) : (
            <div className="space-y-1">
              {filteredLogs.map((log, idx) => (
                <div key={idx} className={getLogColor(log.level)}>
                  <span className="text-arx-muted">{log.timestamp}</span> [{log.level}]
                  {log.module && (
                    <span className="text-arx-blue mx-1">{log.module}</span>
                  )}
                  {log.message}
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </TabsContent>

      <TabsContent value="Memory" className="flex-1 flex flex-col min-h-0 mt-0 data-[state=inactive]:hidden">
        <div className="border-b border-arx-border p-3 space-y-2">
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="arx-glass p-2 rounded-lg text-center">
              <div className="text-arx-blue font-bold">{memoryStats.total}</div>
              <div className="text-arx-muted text-[10px]">Total</div>
            </div>
            <div className="arx-glass p-2 rounded-lg text-center">
              <div className="text-arx-cyan font-bold">{memoryStats.files}</div>
              <div className="text-arx-muted text-[10px]">Files</div>
            </div>
            <div className="arx-glass p-2 rounded-lg text-center">
              <div className="text-arx-green font-bold">{memoryStats.session_turns}</div>
              <div className="text-arx-muted text-[10px]">Turns</div>
            </div>
          </div>

          <Input
            placeholder="Search memory..."
            value={memoryQuery}
            onChange={(e) => setMemoryQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && memoryQuery) {
                sendCommand(`recall ${memoryQuery}`)
              }
            }}
            className="h-7 text-xs bg-arx-input border-arx-border"
          />
        </div>

        <ScrollArea className="flex-1 p-3">
          {memoryStats.recent?.length === 0 ? (
            <div className="text-arx-muted text-xs">No memories yet</div>
          ) : (
            <div className="space-y-2">
              {memoryStats.recent?.map((mem, idx) => (
                <div key={idx} className="text-xs arx-glass p-2 rounded-lg">
                  <div className="text-arx-text font-semibold">{mem.title}</div>
                  <div className="text-arx-muted mt-0.5">{mem.content}</div>
                  <div className="text-[10px] text-arx-muted mt-1">{mem.timestamp}</div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </TabsContent>
    </Tabs>
  )
}

export default StreamTabs
