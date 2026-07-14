import { useAppStore } from '../store/useAppStore'

export const useSystemStats = () => {
  const { systemStats, statsHistory } = useAppStore()

  const getStatHistory = (stat) => {
    return statsHistory[stat] || []
  }

  const getStatAverage = (stat) => {
    const history = getStatHistory(stat)
    if (history.length === 0) return 0
    return Math.round(history.reduce((a, b) => a + b, 0) / history.length)
  }

  const getStatMax = (stat) => {
    const history = getStatHistory(stat)
    if (history.length === 0) return 0
    return Math.max(...history)
  }

  const getStatMin = (stat) => {
    const history = getStatHistory(stat)
    if (history.length === 0) return 0
    return Math.min(...history)
  }

  return {
    systemStats,
    statsHistory,
    getStatHistory,
    getStatAverage,
    getStatMax,
    getStatMin,
  }
}
