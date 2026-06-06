import React from 'react'
import './VoiceWaveform.css'

export default function VoiceWaveform({ levels = [] }) {
  const points = levels && levels.length > 0 ? levels : Array(32).fill(0.2)

  // Create SVG path for smooth waveform
  const pathData = points
    .map((level, i) => {
      const x = (i / (points.length - 1)) * 100
      const y = 50 - (level || 0) * 40
      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
    })
    .join(' ')

  return (
    <svg className="waveform" viewBox="0 0 100 100" preserveAspectRatio="none">
      <path className="waveform-line" d={pathData} />
    </svg>
  )
}
