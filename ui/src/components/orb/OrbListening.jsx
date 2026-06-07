import React from 'react'
import { motion } from 'framer-motion'
import VoiceWaveform from './VoiceWaveform'

const OrbListening = () => {
  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <motion.div
        className="relative w-48 h-48"
        animate={{ scale: [1, 1.05, 1] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        {/* Outer ring glow */}
        <motion.div
          className="absolute inset-0 rounded-full border-2 border-arx-cyan/50"
          animate={{ opacity: [0.3, 0.8, 0.3] }}
          transition={{ duration: 2, repeat: Infinity }}
        />

        {/* Middle ring */}
        <div className="absolute inset-4 rounded-full border border-arx-blue/40" />

        {/* Inner orb */}
        <div className="absolute inset-8 rounded-full bg-gradient-to-b from-arx-blue to-arx-orb flex items-center justify-center shadow-2xl">
          <motion.div
            className="text-5xl"
            animate={{ rotate: 360 }}
            transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
          >
            △
          </motion.div>
        </div>

        {/* Listening text */}
        <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-arx-cyan text-sm font-semibold tracking-widest">
          LISTENING...
        </div>
      </motion.div>

      <VoiceWaveform />
    </div>
  )
}

export default OrbListening
