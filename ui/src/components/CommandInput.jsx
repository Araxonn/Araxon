import React, { useState } from 'react'
import { Paperclip, Mic, Send } from 'lucide-react'
import './CommandInput.css'

export default function CommandInput({ onSendCommand = () => {} }) {
  const [input, setInput] = useState('')

  const quickCommands = ['Open VS Code', 'Summarize Notes', 'Show System Status', 'Run Morning Routine', 'Search Files']

  const handleSend = (text) => {
    if (text.trim()) {
      onSendCommand(text)
      setInput('')
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend(input)
    }
  }

  return (
    <div className="command-input-container">
      <div className="input-section">
        <button className="icon-btn" title="Attach">
          <Paperclip size={18} />
        </button>
        <button className="icon-btn" title="Mic">
          <Mic size={18} />
        </button>
        <input
          type="text"
          placeholder="Ask Araxon anything or give a command..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          className="command-input"
        />
        <button className="send-btn" onClick={() => handleSend(input)}>
          <Send size={18} />
        </button>
      </div>

      <div className="quick-commands">
        {quickCommands.map((cmd, idx) => (
          <button
            key={idx}
            className="command-chip"
            onClick={() => handleSend(cmd)}
          >
            {cmd}
          </button>
        ))}
      </div>
    </div>
  )
}
