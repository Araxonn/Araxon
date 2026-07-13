import React from 'react'
import { motion } from 'framer-motion'
import { Code2 } from 'lucide-react'
import VoiceWaveform from './VoiceWaveform'

const OrbCodeMode = () => {
  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <motion.div
        className="relative w-48 h-48"
        animate={{ scale: [1, 1.02, 1] }}
        transition={{ duration: 2.5, repeat: Infinity }}
      >
        <motion.div
          className="absolute inset-0 rounded-full border-2 border-arx-purple/40 shadow-[0_0_20px_rgba(139,92,246,0.3)]"
          animate={{ opacity: [0.4, 0.8, 0.4] }}
          transition={{ duration: 2, repeat: Infinity }}
        />

        <div className="absolute inset-4 rounded-full border border-arx-purple/20" />

        <div className="absolute inset-7 rounded-full bg-gradient-to-b from-arx-purple/30 via-arx-orb/40 to-arx-bg shadow-arx-inner flex items-center justify-center overflow-hidden">
          <VoiceWaveform />
          <div className="relative z-10">
            <Code2 className="text-arx-purple w-10 h-10 drop-shadow-[0_0_8px_rgba(139,92,246,0.6)]" />
          </div>
        </div>

        <div className="absolute -bottom-10 left-1/2 -translate-x-1/2">
          <span className="arx-status-pill bg-arx-purple/10 text-arx-purple border border-arx-purple/30">
            <span className="w-1.5 h-1.5 bg-arx-purple rounded-full" />
            Code Mode Active
          </span>
        </div>
      </motion.div>
    </div>
  )
}

export default OrbCodeMode
