import React, { useRef, useEffect } from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useWebSocket } from '../../hooks/useWebSocket'
import { ScrollArea } from '../ui/scroll-area'
import { Button } from '../ui/button'
import { FileText, Trash2, FolderOpen } from 'lucide-react'

const FilesPanel = () => {
  const { ingestedFiles } = useAppStore()
  const { sendCommand, sendFileIngest, sendNavChange } = useWebSocket()
  const fileInputRef = useRef(null)

  useEffect(() => {
    sendNavChange('Files')
  }, [sendNavChange])

  const handleIngestFile = async (e) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        const content = event.target?.result
        sendFileIngest(content, file.name)
      }
      reader.readAsText(file)
    }
  }

  const handleRemoveFile = (name) => {
    sendCommand(`remove file ${name}`)
  }

  return (
    <div className="flex flex-col h-full bg-arx-bg border-l border-arx-border">
      <div className="px-4 py-3 border-b border-arx-border">
        <h2 className="text-[11px] font-bold text-arx-text tracking-widest">FILES</h2>
      </div>

      <div className="flex-1 min-h-0 overflow-hidden">
        <ScrollArea className="h-full w-full p-3">
          {ingestedFiles.length === 0 ? (
            <div className="text-center text-arx-muted text-sm py-8">
              No files ingested yet
            </div>
          ) : (
            <div className="space-y-2">
              {ingestedFiles.map((file, idx) => (
                <div
                  key={idx}
                  className="p-2 bg-arx-card rounded border border-arx-border flex items-center justify-between group hover:bg-arx-active transition-colors"
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <FileText size={14} className="text-arx-blue flex-shrink-0" />
                    <div className="min-w-0">
                      <div className="text-xs font-semibold text-arx-text truncate">
                        {file.name}
                      </div>
                      <div className="text-xs text-arx-muted">
                        {file.size ? `${(file.size / 1024).toFixed(2)} KB • ` : ''}
                        {file.date ? new Date(file.date).toLocaleString() : 'Ingested'}
                      </div>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={() => handleRemoveFile(file.name)}
                  >
                    <Trash2 size={12} />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </div>

      <div className="border-t border-arx-border p-3 space-y-2">
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleIngestFile}
          className="hidden"
          accept=".txt,.md,.py,.pdf,.json,.jsx,.tsx,.js,.ts"
        />
        <Button
          size="sm"
          className="w-full h-7 text-xs"
          onClick={() => fileInputRef.current?.click()}
        >
          <FileText size={12} className="mr-1" />
          Ingest File
        </Button>
        <Button
          variant="outline"
          size="sm"
          className="w-full h-7 text-xs"
          onClick={() => sendCommand('ingest my files')}
        >
          <FolderOpen size={12} className="mr-1" />
          Ingest Folder
        </Button>
      </div>
    </div>
  )
}

export default FilesPanel
