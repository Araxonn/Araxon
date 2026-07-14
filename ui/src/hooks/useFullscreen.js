import { useEffect, useState } from 'react'
import { useAppStore } from '../store/useAppStore'

export const useFullscreen = () => {
  const { isFullscreen, toggleFullscreen } = useAppStore()

  const toggleFullscreenMode = async () => {
    try {
      // Try Tauri API first
      try {
        const { appWindow } = await import('@tauri-apps/api/window')
        await appWindow.setFullscreen(!isFullscreen)
      } catch (err) {
        // Fallback to browser API
        if (!document.fullscreenElement) {
          await document.documentElement.requestFullscreen()
        } else {
          await document.exitFullscreen()
        }
      }
      toggleFullscreen()
    } catch (err) {
      console.error('Fullscreen error:', err)
    }
  }

  return { isFullscreen, toggleFullscreenMode }
}

export const useMinimize = () => {
  const minimize = async () => {
    try {
      const { appWindow } = await import('@tauri-apps/api/window')
      await appWindow.minimize()
    } catch (err) {
      console.error('Minimize not available in browser mode')
    }
  }

  return { minimize }
}
