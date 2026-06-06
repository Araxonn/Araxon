import React, { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import './AIOrb.css'

export default function AIOrb({ state = 'standby', waveformLevels = [] }) {
  const canvasRef = useRef(null)
  const animationFrameRef = useRef(null)

  // Determine colors based on state
  const getColors = () => {
    switch (state) {
      case 'listening':
        return { ring: '#06B6D4', text: '#06B6D4', glow: '#0891b2' }
      case 'thinking':
        return { ring: '#8B5CF6', text: '#8B5CF6', glow: '#7c3aed' }
      case 'speaking':
        return { ring: '#10B981', text: '#10B981', glow: '#059669' }
      case 'processing':
        return { ring: '#F59E0B', text: '#F59E0B', glow: '#d97706' }
      default:
        return { ring: '#3B82F6', text: '#3B82F6', glow: '#1d4ed8' }
    }
  }

  const colors = getColors()
  const rotationSpeed = state === 'thinking' ? 6 : state === 'processing' ? 8 : 8

  // Draw waveform on canvas
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const width = canvas.width
    const height = canvas.height
    const centerX = width / 2
    const centerY = height / 2

    const animate = () => {
      // Clear canvas
      ctx.fillStyle = 'rgba(8, 11, 20, 0.1)'
      ctx.fillRect(0, 0, width, height)

      // Draw waveform
      ctx.strokeStyle = colors.ring
      ctx.lineWidth = 2
      ctx.beginPath()

      const points = waveformLevels && waveformLevels.length > 0 ? waveformLevels : Array(32).fill(0.2)
      const pointSpacing = width / points.length

      for (let i = 0; i < points.length; i++) {
        const x = (i * pointSpacing) + pointSpacing / 2
        const amplitude = (points[i] || 0) * 40
        const y = centerY - amplitude + (Math.sin(i / 2) * amplitude * 0.3)

        if (i === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      }

      ctx.stroke()

      // Draw bottom mirror
      for (let i = points.length - 1; i >= 0; i--) {
        const x = (i * pointSpacing) + pointSpacing / 2
        const amplitude = (points[i] || 0) * 40
        const y = centerY + amplitude + (Math.sin(i / 2) * amplitude * 0.3)
        ctx.lineTo(x, y)
      }

      ctx.closePath()
      ctx.fillStyle = `${colors.ring}11`
      ctx.fill()

      animationFrameRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [waveformLevels, colors])

  return (
    <div className="orb-container">
      <motion.div
        className="orb-wrapper"
        animate={{ rotate: 360 }}
        transition={{ duration: 60 / rotationSpeed, repeat: Infinity, ease: 'linear' }}
      >
        <svg className="orb-ring outer" viewBox="0 0 400 400">
          <circle cx="200" cy="200" r="180" stroke={colors.ring} strokeWidth="2" fill="none" opacity="0.8" />
          <defs>
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <circle cx="200" cy="200" r="180" stroke={colors.ring} strokeWidth="2" fill="none" opacity="0.3" filter="url(#glow)" />
        </svg>

        <motion.svg
          className="orb-ring middle"
          viewBox="0 0 400 400"
          animate={{ rotate: -360 }}
          transition={{ duration: 90, repeat: Infinity, ease: 'linear' }}
        >
          <circle cx="200" cy="200" r="150" stroke={colors.ring} strokeWidth="1" fill="none" opacity="0.4" strokeDasharray="8 4" />
        </motion.svg>
      </motion.div>

      <canvas
        ref={canvasRef}
        className="waveform-canvas"
        width={380}
        height={380}
      />

      <div className="orb-center">
        <svg className="orb-logo" viewBox="0 0 100 100">
          <polygon points="50,10 90,90 10,90" fill="none" stroke="#F1F5F9" strokeWidth="2" />
        </svg>

        {/* Particles */}
        {Array.from({ length: 20 }).map((_, i) => {
          const angle = (i / 20) * Math.PI * 2
          const distance = 80 + Math.sin(i) * 10
          const x = Math.cos(angle) * distance
          const y = Math.sin(angle) * distance
          return (
            <div
              key={i}
              className="particle"
              style={{
                left: `calc(50% + ${x}px)`,
                top: `calc(50% + ${y}px)`,
                animationDelay: `${i * 0.1}s`,
              }}
            />
          )
        })}
      </div>

      <div className="orb-label">
        <motion.div className="status-indicator" animate={{ opacity: [1, 0.6, 1] }} transition={{ duration: 2, repeat: Infinity }} style={{ backgroundColor: colors.text }} />
        <span className="status-text">{state.toUpperCase()}...</span>
      </div>
    </div>
  )
}
