import { useEffect, useState } from 'react'

export const useUptime = () => {
  const [uptime, setUptime] = useState(0)

  useEffect(() => {
    const startTime = Date.now()

    const interval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000)
      setUptime(elapsed)
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  const formatUptime = () => {
    const hours = Math.floor(uptime / 3600)
    const minutes = Math.floor((uptime % 3600) / 60)
    const seconds = uptime % 60

    if (hours > 0) {
      return `${hours}h ${minutes}m ${seconds}s`
    }
    if (minutes > 0) {
      return `${minutes}m ${seconds}s`
    }
    return `${seconds}s`
  }

  return {
    uptime,
    formattedUptime: formatUptime(),
  }
}
