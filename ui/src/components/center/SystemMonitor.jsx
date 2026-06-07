import React, { useState } from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useSystemStats } from '../../hooks/useSystemStats'
import { Button } from '../ui/button'
import Sparkline from './Sparkline'
import { Cpu, Database, HardDrive, Zap, MonitorPlay, Wifi } from 'lucide-react'

const MetricCard = ({ label, value, icon: Icon, color, onClick }) => {
  return (
    <Button
      variant="ghost"
      className="flex-1 p-3 h-24 flex flex-col items-start justify-between border border-arx-border rounded hover:bg-arx-active cursor-pointer transition-all"
      onClick={onClick}
    >
      <div className="flex items-center gap-2 w-full">
        <Icon size={16} className={color} />
        <span className="text-xs text-arx-muted">{label}</span>
      </div>
      <div className={`text-2xl font-bold ${color}`}>{value}%</div>
    </Button>
  )
}

const SystemMonitor = ({ onMetricClick }) => {
  const { systemStats } = useSystemStats()

  const metrics = [
    {
      id: 'cpu',
      label: 'CPU',
      value: systemStats.cpu,
      icon: Cpu,
      color: 'text-arx-blue',
    },
    {
      id: 'ram',
      label: 'RAM',
      value: systemStats.ram,
      icon: Database,
      color: 'text-arx-cyan',
    },
    {
      id: 'gpu',
      label: 'GPU',
      value: systemStats.gpu,
      icon: MonitorPlay,
      color: 'text-arx-green',
    },
    {
      id: 'net',
      label: 'NET',
      value: Math.round(systemStats.net),
      icon: Wifi,
      color: 'text-arx-orange',
    },
    {
      id: 'disk',
      label: 'DISK',
      value: systemStats.disk,
      icon: HardDrive,
      color: 'text-arx-purple',
    },
    {
      id: 'battery',
      label: 'BATTERY',
      value: systemStats.battery,
      icon: Zap,
      color: 'text-arx-green',
    },
  ]

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-6 gap-2">
        {metrics.map(({ id, ...metric }) => (
          <MetricCard
            key={id}
            {...metric}
            onClick={() => onMetricClick(id)}
          />
        ))}
      </div>
    </div>
  )
}

export default SystemMonitor
