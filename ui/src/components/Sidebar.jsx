import React from 'react'
import {
  LayoutDashboard,
  Bot,
  Brain,
  Zap,
  Mic,
  Eye,
  Terminal,
  Puzzle,
  Settings,
  Radio,
  Headphones,
  Play,
  Cpu,
  Smartphone,
} from 'lucide-react'
import './Sidebar.css'

export default function Sidebar({ activeNav, setActiveNav, activeMode, setActiveMode }) {
  const workspaceItems = [
    { id: 'Dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'Agents', label: 'Agents', icon: Bot },
    { id: 'Memory', label: 'Memory', icon: Brain },
    { id: 'Automation', label: 'Automation', icon: Zap },
    { id: 'Voice', label: 'Voice', icon: Mic },
    { id: 'Vision', label: 'Vision', icon: Eye },
    { id: 'Terminal', label: 'Terminal', icon: Terminal },
    { id: 'Plugins', label: 'Plugins', icon: Puzzle },
    { id: 'Settings', label: 'Settings', icon: Settings },
  ]

  const modes = [
    { id: 'Observe Mode', label: 'Observe Mode', icon: Radio },
    { id: 'Assist Mode', label: 'Assist Mode', icon: Headphones },
    { id: 'Execute Mode', label: 'Execute Mode', icon: Play },
    { id: 'Autonomous Mode', label: 'Autonomous Mode', icon: Cpu },
  ]

  const routines = [
    'Morning Routine',
    'Coding Setup',
    'Study Mode',
    'Gaming Mode',
  ]

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="12 2 19 21 5 21"></polygon>
          </svg>
          <span>ARAXON AI</span>
        </div>
        <button className="settings-btn">
          <Settings size={18} />
        </button>
      </div>

      <div className="sidebar-section">
        <h3 className="section-title">WORKSPACE</h3>
        <nav className="nav-items">
          {workspaceItems.map((item) => {
            const Icon = item.icon
            return (
              <button
                key={item.id}
                className={`nav-item ${activeNav === item.id ? 'active' : ''}`}
                onClick={() => setActiveNav(item.id)}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            )
          })}
        </nav>
      </div>

      <div className="sidebar-section">
        <h3 className="section-title">MODES</h3>
        <div className="mode-items">
          {modes.map((mode) => {
            const Icon = mode.icon
            const isActive = activeMode === mode.id
            return (
              <button
                key={mode.id}
                className={`mode-item ${isActive ? 'active' : ''}`}
                onClick={() => setActiveMode(mode.id)}
              >
                <Icon size={18} />
                <span>{mode.label}</span>
                {isActive && <div className="mode-indicator"></div>}
              </button>
            )
          })}
        </div>
      </div>

      <div className="sidebar-section">
        <h3 className="section-title">ROUTINES</h3>
        <div className="routine-items">
          {routines.map((routine, idx) => (
            <button key={idx} className="routine-item">
              {routine}
            </button>
          ))}
          <button className="routine-item new-routine">
            <span>+</span> Create New Routine
          </button>
        </div>
      </div>

      <div className="sidebar-section">
        <h3 className="section-title">CONNECT</h3>
        <div className="connect-items">
          <button className="connect-item">
            <Smartphone size={18} />
            <span>Mobile Link</span>
          </button>
          <div className="core-status">
            <div className="status-dot"></div>
            <div className="status-text">
              <div className="status-name">Araxon Core</div>
              <div className="status-version">v2.0.0</div>
            </div>
          </div>
        </div>
      </div>

      <div className="sidebar-footer">
        <div className="footer-status">
          <div className="status-dot online"></div>
          <span>ONLINE</span>
          <span className="separator">|</span>
          <span>Araxon Core: Active</span>
        </div>
      </div>
    </aside>
  )
}
