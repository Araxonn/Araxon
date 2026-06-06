import React from 'react'
import { CheckCircle2, Loader } from 'lucide-react'
import './AgentSteps.css'

export default function AgentSteps({ steps = [] }) {
  if (!steps || steps.length === 0) {
    return null
  }

  return (
    <div className="agent-steps">
      {steps.map((step, idx) => {
        const isDone = step.done || step.status === 'done'
        const isRunning = step.status === 'running'

        return (
          <div key={idx} className={`step ${isDone ? 'done' : isRunning ? 'running' : 'pending'}`}>
            <div className="step-indicator">
              {isDone ? (
                <CheckCircle2 size={16} className="check-icon" />
              ) : isRunning ? (
                <Loader size={16} className="loader-icon" />
              ) : (
                <div className="circle-icon" />
              )}
            </div>
            <span className={`step-text ${isDone ? 'line-through' : ''}`}>
              {step.step_number}. {step.description}
            </span>
            {isDone && <span className="step-badge">Done</span>}
          </div>
        )
      })}
    </div>
  )
}
