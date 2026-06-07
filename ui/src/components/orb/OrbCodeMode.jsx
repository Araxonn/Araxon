import React from 'react'
import { motion } from 'framer-motion'
import { Code2 } from 'lucide-react'

const OrbCodeMode = () => {
  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <motion.div
        className="relative w-48 h-48"
        animate={{ scale: [1, 1.03, 1] }}
        transition={{ duration: 2.5, repeat: Infinity }}
      >
        {/* Pulsing rings */}
        <motion.div
          className="absolute inset-0 rounded-full border-2 border-arx-purple/50"
          animate={{ scale: [1, 1.2], opacity: [1, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
        />

        <motion.div
          className="absolute inset-4 rounded-full border border-arx-purple/30"
          animate={{ scale: [1.2, 1], opacity: [0, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        />

        {/* Inner orb */}
        <div className="absolute inset-8 rounded-full bg-gradient-to-b from-arx-purple to-arx-orb flex items-center justify-center shadow-2xl">
          <Code2 className="text-white text-4xl" />
        </div>

        {/* Code mode text */}
        <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-arx-purple text-sm font-semibold tracking-widest">
          CODE MODE
        </div>
      </motion.div>

      {/* Syntax highlight indicator */}
      <div className="text-center text-xs text-arx-secondary font-mono">
        <div className="text-arx-purple">{'<'}</div>
        <div>Ready for analysis</div>
        <div className="text-arx-purple">{'>'}</div>
      </div>
    </div>
  )
}

export default OrbCodeMode
