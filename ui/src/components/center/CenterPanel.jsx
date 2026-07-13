import React, { useState } from 'react'
import AIOrb from '../orb/AIOrb'
import QuickActions from './QuickActions'
import SystemMonitor from './SystemMonitor'
import CommandInput from './CommandInput'
import CenterGreeting from '../layout/CenterGreeting'
import CodeEditor from '../panels/CodePanel'
import MetricDetailOverlay from '../overlays/MetricDetailOverlay'
import { useSystemStats } from '../../hooks/useSystemStats'
import { useAppStore } from '../../store/useAppStore'

const CenterPanel = () => {
  const [selectedMetric, setSelectedMetric] = useState(null)
  const { getStatHistory } = useSystemStats()
  const { araxonState } = useAppStore()

  const metricLabels = {
    cpu: 'CPU',
    ram: 'RAM',
    gpu: 'GPU',
    net: 'Network',
    disk: 'Disk',
    battery: 'Battery',
  }

  const isCodeMode = araxonState === 'code'

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-arx-bg bg-arx-radial relative">
      <div className="absolute inset-0 bg-arx-grid bg-grid opacity-40 pointer-events-none" />

      <CenterGreeting />

      <div className="flex-1 flex flex-col min-h-0 relative z-10">
        {/* Orb / Visualizer */}
        <div
          className={`flex items-center justify-center px-4 ${
            isCodeMode ? 'py-4 flex-shrink-0' : 'flex-1 py-6'
          }`}
        >
          <AIOrb />
        </div>

        <QuickActions />

        {/* Code editor in code mode */}
        {isCodeMode && (
          <div className="flex-1 min-h-0 mx-4 mb-2 arx-panel rounded-xl overflow-hidden">
            <CodeEditor embedded />
          </div>
        )}

        <div className="px-4 py-3 border-t border-arx-border/60">
          <SystemMonitor
            onMetricClick={(metric) => setSelectedMetric(metric)}
          />
        </div>

        <CommandInput />
      </div>

      {selectedMetric && (
        <MetricDetailOverlay
          metric={selectedMetric}
          label={metricLabels[selectedMetric]}
          history={getStatHistory(selectedMetric)}
          onClose={() => setSelectedMetric(null)}
        />
      )}
    </div>
  )
}

export default CenterPanel
