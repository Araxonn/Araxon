import React from 'react'
import { motion } from 'framer-motion'
import { useAppStore } from '../../store/useAppStore'
import VoiceWaveform from './VoiceWaveform'
import ArxonLogo from '../ui/ArxonLogo'

const OrbExecuting = () => {
  const { executionProgress } = useAppStore()
  const progress = executionProgress || 75

  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <motion.div
        className="relative w-56 h-56"
        animate={{ scale: [1, 1.02, 1] }}
        transition={{ duration: 1.5, repeat: Infinity }}
      >
        <svg className="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="46"
            fill="none"
            stroke="rgba(30,41,59,0.5)"
            strokeWidth="3"
          />
          <motion.circle
            cx="50"
            cy="50"
            r="46"
            fill="none"
            stroke="url(#progressGradient)"
            strokeWidth="3"
            strokeLinecap="round"
            strokeDasharray={`${progress * 2.89} 289`}
            initial={{ strokeDasharray: '0 289' }}
            animate={{ strokeDasharray: `${progress * 2.89} 289` }}
            transition={{ duration: 1 }}
          />
          <defs>
            <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#3B82F6" />
              <stop offset="100%" stopColor="#06B6D4" />
            </linearGradient>
          </defs>
        </svg>

        <motion.div
          className="absolute inset-2 rounded-full border border-arx-blue/30"
          animate={{ rotate: 360 }}
          transition={{ duration: 12, repeat: Infinity, ease: 'linear' }}
        />

        <div className="absolute inset-8 rounded-full bg-gradient-to-b from-arx-blue/25 via-arx-orb/50 to-arx-bg shadow-arx-inner flex items-center justify-center overflow-hidden">
          <VoiceWaveform />
          <div className="relative z-10 text-center">
            <div className="text-3xl font-bold text-arx-cyan-bright">{progress}%</div>
          </div>
        </div>

        <div className="absolute -bottom-10 left-1/2 -translate-x-1/2">
          <span className="arx-status-pill bg-arx-green/10 text-arx-green border border-arx-green/30">
            <span className="w-1.5 h-1.5 bg-arx-green rounded-full animate-pulse" />
            Executing...
          </span>
        </div>
      </motion.div>
    </div>
  )
}

export default OrbExecuting
