import React, { useState, useEffect } from 'react'
import { Mic, Radio, Settings } from 'lucide-react'
import './StatusBar.css'

export default function StatusBar({ startTime = Date.now() }) {
  const [uptime, setUptime] = useState('0h 0m 0s')

  useEffect(() => {
    const interval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000)
      const hours = Math.floor(elapsed / 3600)
      const minutes = Math.floor((elapsed % 3600) / 60)
      const seconds = elapsed % 60
      setUptime(`${hours}h ${minutes}m ${seconds}s`)
    }, 1000)

    return () => clearInterval(interval)
  }, [startTime])

  return (
    <div className="status-bar">
      <div className="status-left">
        <div className="status-dot online"></div>
        <span className="status-label">ONLINE</span>
        <span className="separator">|</span>
        <span>Araxon Core: Active</span>
      </div>

      <div className="status-center">
        <span>Uptime: {uptime}</span>
      </div>

      <div className="status-right">
        <div className="status-item">
          <Mic size={14} />
          <span>Mic: On</span>
        </div>
        <div className="separator">|</div>
        <div className="status-item">
          <Radio size={14} />
          <span>Voice: On</span>
        </div>
        <div className="separator">|</div>
        <div className="status-item">
          <Settings size={14} />
          <span>Mem: 72%</span>
        </div>
      </div>
    </div>
  )
}
