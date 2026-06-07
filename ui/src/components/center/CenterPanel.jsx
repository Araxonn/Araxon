import React, { useState } from 'react'
import AIOrb from '../orb/AIOrb'
import QuickActions from './QuickActions'
import SystemMonitor from './SystemMonitor'
import CommandInput from './CommandInput'
import MetricDetailOverlay from '../overlays/MetricDetailOverlay'
import { useSystemStats } from '../../hooks/useSystemStats'
import { ScrollArea } from '../ui/scroll-area'

const CenterPanel = () => {
  const [selectedMetric, setSelectedMetric] = useState(null)
  const { getStatHistory } = useSystemStats()

  const metricLabels = {
    cpu: 'CPU',
    ram: 'RAM',
    gpu: 'GPU',
    net: 'Network',
    disk: 'Disk',
    battery: 'Battery',
  }

  return (
    <ScrollArea className="flex-1 flex flex-col bg-arx-bg">
      <div className="flex-1 flex flex-col">
        {/* AI Orb */}
        <div className="flex-1 flex items-center justify-center py-8 px-4">
          <AIOrb />
        </div>

        {/* Quick Actions */}
        <QuickActions />

        {/* System Monitor */}
        <div className="px-4 py-4 border-t border-arx-border">
          <SystemMonitor
            onMetricClick={(metric) => {
              setSelectedMetric(metric)
            }}
          />
        </div>

        {/* Command Input */}
        <CommandInput />
      </div>

      {/* Metric Detail Modal */}
      {selectedMetric && (
        <MetricDetailOverlay
          metric={selectedMetric}
          label={metricLabels[selectedMetric]}
          history={getStatHistory(selectedMetric)}
          onClose={() => setSelectedMetric(null)}
        />
      )}
    </ScrollArea>
  )
}

export default CenterPanel
