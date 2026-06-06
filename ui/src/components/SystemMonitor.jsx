import React from 'react'
import { LineChart, Line, ResponsiveContainer } from 'recharts'
import './SystemMonitor.css'

export default function SystemMonitor({ stats = {}, history = {} }) {
  const metrics = [
    { key: 'cpu', label: 'CPU', color: '#3B82F6', unit: '%' },
    { key: 'ram', label: 'RAM', color: '#06B6D4', unit: '%' },
    { key: 'gpu', label: 'GPU', color: '#8B5CF6', unit: '%' },
    { key: 'net', label: 'NET', color: '#10B981', unit: ' GB/s' },
    { key: 'disk', label: 'DISK', color: '#F59E0B', unit: '%' },
    { key: 'battery', label: 'BATTERY', color: '#14B8A6', unit: '%' },
  ]

  return (
    <div className="system-monitor">
      {metrics.map((metric) => {
        const value = stats[metric.key] || 0
        const data = (history[metric.key] || []).map((v) => ({ value: v }))

        return (
          <div key={metric.key} className="metric">
            <div className="metric-bar">
              <div
                className="metric-bar-fill"
                style={{
                  width: `${Math.min(100, value)}%`,
                  backgroundColor: metric.color,
                }}
              />
            </div>
            <div className="metric-label">{metric.label}</div>
            <div className="metric-value" style={{ color: metric.color }}>
              {typeof value === 'number' ? value.toFixed(1) : value}
              {metric.unit}
            </div>
            {data.length > 0 && (
              <ResponsiveContainer width="100%" height={30}>
                <LineChart data={data}>
                  <Line type="monotone" dataKey="value" stroke={metric.color} dot={false} isAnimationActive={false} strokeWidth={1} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        )
      })}
    </div>
  )
}
