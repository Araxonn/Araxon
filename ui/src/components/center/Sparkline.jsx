import React from 'react'
import {
  LineChart,
  Line,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'

const Sparkline = ({ data = [], color = '#3B82F6', height = 80 }) => {
  const chartData = data.slice(-20).map((value, idx) => ({
    value,
    index: idx,
  }))

  if (chartData.length === 0) {
    return (
      <div
        style={{ height }}
        className="bg-arx-card rounded flex items-center justify-center text-arx-muted text-xs"
      >
        No data
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart
        data={chartData}
        margin={{ top: 5, right: 5, bottom: 0, left: 0 }}
      >
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
          stroke={color}
          dot={false}
          strokeWidth={2}
          isAnimationActive
        />
      </LineChart>
    </ResponsiveContainer>
  )
}

export default Sparkline
