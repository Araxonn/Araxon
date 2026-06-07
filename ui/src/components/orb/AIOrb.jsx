import React from 'react'
import { useAppStore } from '../../store/useAppStore'
import OrbListening from './OrbListening'
import OrbExecuting from './OrbExecuting'
import OrbCodeMode from './OrbCodeMode'

const AIOrb = () => {
  const { araxonState } = useAppStore()

  return (
    <div className="flex items-center justify-center h-full">
      {araxonState === 'executing' && <OrbExecuting />}
      {araxonState === 'code' && <OrbCodeMode />}
      {(araxonState === 'listening' || araxonState === 'thinking') && (
        <OrbListening />
      )}
    </div>
  )
}

export default AIOrb
