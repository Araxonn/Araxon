import React from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogClose,
} from '../ui/dialog'
import { Button } from '../ui/button'
import {
  LineChart,
  Line,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'
import { X } from 'lucide-react'

const MetricDetailOverlay = ({ metric, label, history, onClose }) => {
  const chartData = history.slice(-60).map((value, idx) => ({
    value,
    index: idx,
  }))

  const avg = Math.round(history.reduce((a, b) => a + b, 0) / history.length)
  const max = Math.max(...history, 0)
  const min = Math.min(...history, 0)
  const current = history[history.length - 1] || 0

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80">
      <div className="bg-arx-card border border-arx-border rounded-lg p-6 w-full max-w-2xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-arx-text">{label}</h2>
            <p className="text-3xl font-bold text-arx-blue mt-2">{current}%</p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={onClose}
          >
            <X size={16} />
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-2 mb-4">
          <div className="p-2 bg-arx-input rounded text-center">
            <div className="text-xs text-arx-muted">Average</div>
            <div className="text-lg font-bold text-arx-cyan">{avg}%</div>
          </div>
          <div className="p-2 bg-arx-input rounded text-center">
            <div className="text-xs text-arx-muted">Max</div>
            <div className="text-lg font-bold text-arx-green">{max}%</div>
          </div>
          <div className="p-2 bg-arx-input rounded text-center">
            <div className="text-xs text-arx-muted">Min</div>
            <div className="text-lg font-bold text-arx-orange">{min}%</div>
          </div>
        </div>

        {/* Chart */}
        <div className="h-64 -mx-2">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 10, bottom: 0, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
              <XAxis dataKey="index" hide />
              <YAxis hide domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0D1220',
                  border: '1px solid #1E293B',
                }}
                formatter={(value) => `${Math.round(value)}%`}
                labelStyle={{ color: '#F1F5F9' }}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#3B82F6"
                dot={false}
                strokeWidth={2}
                isAnimationActive
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-4 flex gap-2 justify-end">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  )
}

export default MetricDetailOverlay
