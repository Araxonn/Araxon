import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle2, Loader2, Circle } from 'lucide-react'
import { Progress } from '../ui/progress'
import { Button } from '../ui/button'

const AgentSteps = ({ steps = [] }) => {
  const [expandedStep, setExpandedStep] = useState(null)

  return (
    <div className="space-y-2">
      {steps.map((step, idx) => {
        const isDone = step.status === 'done'
        const isRunning = step.status === 'running'
        const isPending = step.status === 'pending'

        return (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className="p-2 bg-arx-card rounded border border-arx-border"
          >
            <div className="flex items-center gap-2 cursor-pointer" onClick={() => setExpandedStep(expandedStep === idx ? null : idx)}>
              {isDone && (
                <CheckCircle2 size={16} className="text-arx-green flex-shrink-0" />
              )}
              {isRunning && (
                <Loader2 size={16} className="text-arx-cyan flex-shrink-0 animate-spin" />
              )}
              {isPending && (
                <Circle size={16} className="text-arx-muted flex-shrink-0" />
              )}

              <span className="text-xs font-semibold text-arx-text flex-1 truncate">
                {step.title || `Step ${idx + 1}`}
              </span>

              {isDone && (
                <span className="text-xs text-arx-green font-semibold">Done</span>
              )}
              {isRunning && (
                <span className="text-xs text-arx-cyan font-semibold">
                  {step.percent || 0}%
                </span>
              )}
            </div>

            {isRunning && (
              <div className="mt-2">
                <Progress value={step.percent || 0} />
              </div>
            )}

            {expandedStep === idx && isDone && step.result && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="mt-2 p-2 bg-arx-input rounded text-xs text-arx-secondary font-mono overflow-auto max-h-32"
              >
                {step.result}
              </motion.div>
            )}
          </motion.div>
        )
      })}
    </div>
  )
}

export default AgentSteps
