import React from 'react'
import { useAppStore } from '../../store/useAppStore'
import { motion } from 'framer-motion'

const VoiceWaveform = ({ compact = false }) => {
  const { waveformLevels } = useAppStore()

  const count = compact ? 16 : 48
  const levels =
    waveformLevels.length > 0
      ? waveformLevels.slice(0, count)
      : Array.from({ length: count }, (_, i) =>
          Math.sin(i * 0.5) * 0.3 + 0.4 + Math.random() * 0.2
        )

  if (compact) {
    return (
      <div className="flex items-center justify-center gap-px h-full">
        {levels.map((level, i) => (
          <motion.div
            key={i}
            className="w-0.5 bg-gradient-to-t from-arx-blue to-arx-cyan rounded-full"
            animate={{ height: `${Math.max(2, (level || 0) * 14)}px` }}
            transition={{ duration: 0.15 }}
          />
        ))}
      </div>
    )
  }

  return (
    <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center gap-px w-[70%] h-8 pointer-events-none">
      {levels.map((level, i) => (
        <motion.div
          key={i}
          className="flex-1 bg-gradient-to-t from-arx-blue/80 to-arx-cyan-bright rounded-full min-w-[2px]"
          animate={{ height: `${Math.max(4, (level || 0) * 28)}px` }}
          transition={{ duration: 0.15 }}
        />
      ))}
    </div>
  )
}

export default VoiceWaveform
