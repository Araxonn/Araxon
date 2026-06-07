import React from 'react'
import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'

const OrbExecuting = () => {
  return (
    <div className="flex flex-col items-center justify-center gap-6">
      <motion.div
        className="relative w-48 h-48"
        animate={{ scale: [1, 1.02, 1] }}
        transition={{ duration: 1.5, repeat: Infinity }}
      >
        {/* Rotating rings */}
        <motion.div
          className="absolute inset-0 rounded-full border-2 border-transparent border-t-arx-blue border-r-arx-cyan"
          animate={{ rotate: 360 }}
          transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
        />

        <motion.div
          className="absolute inset-4 rounded-full border-2 border-transparent border-b-arx-green border-l-arx-orange"
          animate={{ rotate: -360 }}
          transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
        />

        {/* Inner orb */}
        <div className="absolute inset-8 rounded-full bg-gradient-to-b from-arx-blue to-arx-orb flex items-center justify-center shadow-2xl">
          <Loader2 className="text-white text-3xl animate-spin" />
        </div>

        {/* Executing text */}
        <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-arx-green text-sm font-semibold tracking-widest">
          EXECUTING...
        </div>
      </motion.div>

      {/* Progress indicator */}
      <div className="w-64 text-center">
        <div className="text-3xl font-bold text-arx-cyan mb-2">75%</div>
        <div className="h-1 bg-arx-card rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-arx-blue to-arx-cyan"
            animate={{ width: '75%' }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>
    </div>
  )
}

export default OrbExecuting
