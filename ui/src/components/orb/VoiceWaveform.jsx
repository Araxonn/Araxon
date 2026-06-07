import React from 'react'
import { useAppStore } from '../../store/useAppStore'
import { motion } from 'framer-motion'

const VoiceWaveform = () => {
  const { waveformLevels } = useAppStore()

  const levels = waveformLevels.slice(0, 40) || Array(40).fill(0)

  return (
    <div className="flex items-center justify-center gap-0.5 h-20">
      {levels.map((level, i) => (
        <motion.div
          key={i}
          className="w-1 bg-gradient-to-t from-arx-blue to-arx-cyan rounded-full"
          animate={{ height: `${Math.max(10, (level || 0) * 60)}px` }}
          transition={{ duration: 0.2 }}
        />
      ))}
    </div>
  )
}

export default VoiceWaveform
