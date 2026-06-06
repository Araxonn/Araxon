import React from 'react'
import AgentSteps from './AgentSteps'
import './CommandStream.css'

export default function CommandStream({ transcript = [], activeTab = 'Commands', setActiveTab = () => {}, agentSteps = [], state = 'standby' }) {
  const tabs = ['Commands', 'Sequences', 'Logs', 'Memory']

  // Separate user and ARAXON messages
  const renderMessage = (msg, idx) => {
    if (msg.speaker === 'user') {
      return (
        <div key={idx} className="message user-message">
          <div className="message-avatar user">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"></path>
            </svg>
          </div>
          <div className="message-content">
            <div className="message-header">
              <span className="message-name">You</span>
              <span className="message-time">
                {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
              </span>
            </div>
            <p className="message-text">{msg.text}</p>
          </div>
        </div>
      )
    }

    // ARAXON message - check for agent steps
    if (msg.text && msg.text.includes('Opening') && agentSteps.length > 0) {
      return (
        <div key={idx} className="message araxon-message">
          <div className="message-avatar araxon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <polygon points="12,2 19,21 5,21"></polygon>
            </svg>
          </div>
          <div className="message-content">
            <div className="message-header">
              <span className="message-name">Araxon AI</span>
              <span className="message-time">
                {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
              </span>
            </div>
            <AgentSteps steps={agentSteps} />
          </div>
        </div>
      )
    }

    return (
      <div key={idx} className="message araxon-message">
        <div className="message-avatar araxon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <polygon points="12,2 19,21 5,21"></polygon>
          </svg>
        </div>
        <div className="message-content">
          <div className="message-header">
            <span className="message-name">Araxon AI</span>
            <span className="message-time">
              {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
            </span>
          </div>
          <p className="message-text">{msg.text}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="command-stream">
      <div className="stream-header">
        <h2>COMMAND STREAM</h2>
        <button className="menu-btn">⋯</button>
      </div>

      <div className="stream-tabs">
        {tabs.map((tab) => (
          <button
            key={tab}
            className={`tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="stream-content">
        {transcript.length === 0 ? (
          <div className="empty-state">
            <p>No commands yet. Ask me something!</p>
          </div>
        ) : (
          transcript.map((msg, idx) => renderMessage(msg, idx))
        )}
      </div>

      <div className="stream-footer">
        <div className="listening-indicator">
          <span>Araxon is listening...</span>
          <div className="mini-waveform">
            {Array.from({ length: 4 }).map((_, i) => (
              <div
                key={i}
                className="waveform-bar"
                style={{
                  animation: `wave ${0.6 + i * 0.1}s ease-in-out infinite`,
                }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
