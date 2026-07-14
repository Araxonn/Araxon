import React, { useEffect } from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useWebSocket } from '../../hooks/useWebSocket'
import { ScrollArea } from '../ui/scroll-area'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogHeader, AlertDialogTitle } from '../ui/alert-dialog'
import { Trash2 } from 'lucide-react'

const MemoryPanel = () => {
  const { memoryStats } = useAppStore()
  const { sendCommand, sendNavChange } = useWebSocket()
  const [query, setQuery] = React.useState('')
  const [showClearDialog, setShowClearDialog] = React.useState(false)

  useEffect(() => {
    sendNavChange('Memory')
  }, [sendNavChange])

  const handleSearch = () => {
    if (query.trim()) {
      sendCommand(`recall ${query}`)
      setQuery('')
    }
  }

  const handleClearAll = () => {
    sendCommand('clear memory')
    setShowClearDialog(false)
  }

  return (
    <div className="flex flex-col h-full bg-arx-bg border-l border-arx-border">
      <div className="px-4 py-3 border-b border-arx-border">
        <h2 className="text-[11px] font-bold text-arx-text tracking-widest">MEMORY</h2>
      </div>
      <div className="border-b border-arx-border p-3 space-y-3">
        <div className="grid grid-cols-3 gap-2 text-xs">
          <div className="bg-arx-card p-2 rounded text-center">
            <div className="text-arx-blue font-bold text-lg">{memoryStats.total}</div>
            <div className="text-arx-muted">Total</div>
          </div>
          <div className="bg-arx-card p-2 rounded text-center">
            <div className="text-arx-cyan font-bold text-lg">{memoryStats.files}</div>
            <div className="text-arx-muted">Files</div>
          </div>
          <div className="bg-arx-card p-2 rounded text-center">
            <div className="text-arx-green font-bold text-lg">{memoryStats.session_turns}</div>
            <div className="text-arx-muted">Turns</div>
          </div>
        </div>

        <div className="flex gap-2">
          <Input
            placeholder="Search memory..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleSearch()
            }}
            className="h-7 text-xs"
          />
          <Button
            size="sm"
            className="h-7 px-2"
            onClick={handleSearch}
            disabled={!query.trim()}
          >
            Search
          </Button>
        </div>
      </div>

      <div className="flex-1 min-h-0 overflow-hidden">
        <ScrollArea className="h-full w-full p-3">
          {memoryStats.recent?.length === 0 ? (
            <div className="text-center text-arx-muted text-sm py-8">
              No memories yet
            </div>
          ) : (
            <div className="space-y-2">
              {memoryStats.recent?.map((mem, idx) => (
                <div key={idx} className="p-2 bg-arx-card rounded border border-arx-border">
                  <div className="text-xs font-semibold text-arx-text">{mem.title}</div>
                  <div className="text-xs text-arx-secondary mt-1">{mem.content}</div>
                  <div className="text-xs text-arx-muted mt-1">{mem.timestamp}</div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </div>

      <div className="border-t border-arx-border p-3">
        <Button
          variant="destructive"
          size="sm"
          className="w-full h-7 text-xs"
          onClick={() => setShowClearDialog(true)}
        >
          <Trash2 size={12} className="mr-1" />
          Clear All Memories
        </Button>
      </div>

      <AlertDialog open={showClearDialog} onOpenChange={setShowClearDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Clear All Memories?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. All memories will be permanently deleted.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <div className="flex gap-2 justify-end">
            <AlertDialogCancel asChild>
              <Button variant="outline" size="sm">
                Cancel
              </Button>
            </AlertDialogCancel>
            <AlertDialogAction asChild>
              <Button variant="destructive" size="sm" onClick={handleClearAll}>
                Clear
              </Button>
            </AlertDialogAction>
          </div>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

export default MemoryPanel
