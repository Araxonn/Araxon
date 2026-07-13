import React from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useSystemStats } from '../../hooks/useSystemStats'
import { Cpu, Database, HardDrive, Zap, MonitorPlay, Wifi } from 'lucide-react'

const MiniSparkline = ({ data = [], color = '#3B82F6' }) => {
  const points = data.slice(-12)
  if (points.length < 2) {
    const fallback = [30, 35, 28, 40, 32, 38, 30, 42, 35, 38, 32, 36]
    return <MiniSparkline data={fallback} color={color} />
  }

  const max = Math.max(...points, 1)
  const min = Math.min(...points, 0)
  const range = max - min || 1
  const w = 48
  const h = 16

  const path = points
    .map((v, i) => {
      const x = (i / (points.length - 1)) * w
      const y = h - ((v - min) / range) * (h - 2) - 1
      return `${i === 0 ? 'M' : 'L'}${x},${y}`
    })
    .join(' ')

  return (
    <svg width={w} height={h} className="opacity-80">
      <path
        d={path}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

const MetricCard = ({ label, value, displayValue, icon: Icon, color, sparkColor, history, onClick }) => {
  return (
    <button
      type="button"
      className="arx-metric-card flex flex-col gap-1 text-left w-full"
      onClick={onClick}
    >
      <div className="flex items-center justify-between w-full">
        <div className="flex items-center gap-1.5">
          <Icon size={12} className={color} />
          <span className="text-[10px] font-semibold text-arx-muted uppercase tracking-wide">
            {label}
          </span>
        </div>
        <MiniSparkline data={history} color={sparkColor} />
      </div>
      <div className={`text-lg font-bold leading-none ${color}`}>
        {displayValue ?? `${value}%`}
      </div>
    </button>
  )
}

const SystemMonitor = ({ onMetricClick }) => {
  const { systemStats } = useSystemStats()
  const { statsHistory } = useAppStore()

  const metrics = [
    {
      id: 'cpu',
      label: 'CPU',
      value: systemStats.cpu,
      icon: Cpu,
      color: 'text-arx-blue',
      sparkColor: '#3B82F6',
    },
    {
      id: 'ram',
      label: 'RAM',
      value: systemStats.ram,
      icon: Database,
      color: 'text-arx-cyan',
      sparkColor: '#06B6D4',
    },
    {
      id: 'gpu',
      label: 'GPU',
      value: systemStats.gpu,
      icon: MonitorPlay,
      color: 'text-arx-green',
      sparkColor: '#10B981',
    },
    {
      id: 'net',
      label: 'NET',
      value: systemStats.net,
      displayValue: `${(systemStats.net / 10).toFixed(1)} GB/s`,
      icon: Wifi,
      color: 'text-arx-orange',
      sparkColor: '#F59E0B',
    },
    {
      id: 'disk',
      label: 'DISK',
      value: systemStats.disk,
      icon: HardDrive,
      color: 'text-arx-purple',
      sparkColor: '#8B5CF6',
    },
    {
      id: 'battery',
      label: 'BATTERY',
      value: systemStats.battery,
      icon: Zap,
      color: 'text-arx-green',
      sparkColor: '#10B981',
    },
  ]

  return (
    <div className="grid grid-cols-6 gap-2">
      {metrics.map(({ id, ...metric }) => (
        <MetricCard
          key={id}
          {...metric}
          history={statsHistory[id] || []}
          onClick={() => onMetricClick(id)}
        />
      ))}
    </div>
  )
}

export default SystemMonitor
