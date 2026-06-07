import React, { useEffect } from 'react'
import { useAppStore } from '../../store/useAppStore'
import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'
import { Button } from '../ui/button'

const NotificationToast = ({ notification, onDismiss }) => {
  useEffect(() => {
    const timer = setTimeout(onDismiss, 4000)
    return () => clearTimeout(timer)
  }, [onDismiss])

  const getIcon = () => {
    switch (notification.type) {
      case 'success':
        return '✓'
      case 'error':
        return '✕'
      case 'warning':
        return '⚠'
      default:
        return 'ℹ'
    }
  }

  const getColors = () => {
    switch (notification.type) {
      case 'success':
        return 'bg-green-500/10 border-green-500/30 text-green-400'
      case 'error':
        return 'bg-red-500/10 border-red-500/30 text-red-400'
      case 'warning':
        return 'bg-orange-500/10 border-orange-500/30 text-orange-400'
      default:
        return 'bg-blue-500/10 border-blue-500/30 text-blue-400'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 400 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 400 }}
      className={`border rounded p-3 text-sm ${getColors()}`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2 flex-1">
          <span className="text-lg mt-0.5">{getIcon()}</span>
          <div className="flex-1">
            <div className="font-semibold">{notification.title}</div>
            <div className="text-xs opacity-80">{notification.message}</div>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="h-6 w-6 p-0 hover:bg-white/10"
          onClick={onDismiss}
        >
          <X size={14} />
        </Button>
      </div>
    </motion.div>
  )
}

const NotificationStack = () => {
  const { notifications, removeNotification } = useAppStore()

  return (
    <div className="fixed top-6 right-6 z-50 flex flex-col gap-2 w-80">
      <AnimatePresence mode="popLayout">
        {notifications.map((notification) => (
          <NotificationToast
            key={notification.id}
            notification={notification}
            onDismiss={() => removeNotification(notification.id)}
          />
        ))}
      </AnimatePresence>
    </div>
  )
}

export default NotificationStack
