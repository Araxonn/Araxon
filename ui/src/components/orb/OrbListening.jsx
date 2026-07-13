import React from 'react'
import { motion } from 'framer-motion'
import VoiceWaveform from './VoiceWaveform'
import ArxonLogo from '../ui/ArxonLogo'

const OrbListening = () => {
  return (
    <div className="flex flex-col items-center justify-center gap-5">
      <motion.div
        className="relative w-56 h-56"
        animate={{ scale: [1, 1.03, 1] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
      >
        <motion.div
          className="absolute -inset-4 rounded-full border border-arx-blue/20"
          animate={{ opacity: [0.2, 0.5, 0.2], scale: [1, 1.05, 1] }}
          transition={{ duration: 3, repeat: Infinity }}
        />

        <motion.div
          className="absolute inset-0 rounded-full border-2 border-arx-cyan/40 shadow-arx-glow"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        />

        <div className="absolute inset-3 rounded-full border border-arx-blue/30" />

        <div className="absolute inset-6 rounded-full bg-gradient-to-b from-arx-blue/20 via-arx-orb/40 to-arx-bg shadow-arx-inner flex items-center justify-center overflow-hidden">
          <VoiceWaveform />
          <div className="relative z-10">
            <ArxonLogo size="lg" className="!w-14 !h-14 !text-lg shadow-arx-glow" />
          </div>
        </div>

        <div className="absolute -bottom-10 left-1/2 -translate-x-1/2">
          <span className="arx-status-pill bg-arx-blue/10 text-arx-cyan border border-arx-cyan/30">
            <span className="w-1.5 h-1.5 bg-arx-cyan rounded-full animate-pulse" />
            Listening...
          </span>
        </div>
      </motion.div>
    </div>
  )
}

export default OrbListening
