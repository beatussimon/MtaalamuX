import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Bell, Check, Trash2 } from 'lucide-react'
import { notificationService } from '../services/api'
import { useNavigate } from 'react-router-dom'

function NotificationsPage() {
  const navigate = useNavigate()
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const response = await notificationService.getAll()
        setNotifications(response.data.results || response.data)
      } catch (error) {
        console.error('Failed to fetch notifications:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchNotifications()
  }, [])

  const handleMarkAsRead = async (id) => {
    try {
      await notificationService.markAsRead(id)
      setNotifications(notifications.map(n => n.id === id ? { ...n, is_read: true } : n))
    } catch (error) {
      console.error('Failed to mark as read:', error)
    }
  }

  const handleMarkAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead()
      setNotifications(notifications.map(n => ({ ...n, is_read: true })))
    } catch (error) {
      console.error('Failed to mark all as read:', error)
    }
  }

  const handleClick = (notification) => {
    if (!notification.is_read) {
      handleMarkAsRead(notification.id)
    }
    if (notification.link) {
      navigate(notification.link)
    }
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
          <Bell className="w-8 h-8 mr-3" />
          Notifications
        </h1>
        {notifications.some(n => !n.is_read) && (
          <button onClick={handleMarkAllAsRead} className="btn-outline text-sm">
            <Check className="w-4 h-4 mr-2" />
            Mark all as read
          </button>
        )}
      </div>

      {loading ? (
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="card p-4 animate-pulse">
              <div className="h-4 bg-gray-200 dark:bg-dark-700 rounded w-3/4" />
            </div>
          ))}
        </div>
      ) : notifications.length > 0 ? (
        <div className="space-y-2">
          {notifications.map((notification) => (
            <motion.div
              key={notification.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              onClick={() => handleClick(notification)}
              className={`card p-4 cursor-pointer transition-colors ${
                notification.is_read
                  ? 'opacity-60'
                  : 'bg-primary-50 dark:bg-primary-900/10 border-l-4 border-primary-500'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-gray-900 dark:text-white">{notification.message}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    {new Date(notification.created_at).toLocaleString()}
                  </p>
                </div>
                {!notification.is_read && (
                  <span className="w-2 h-2 bg-primary-500 rounded-full flex-shrink-0 mt-2" />
                )}
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Bell className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
          <p className="text-gray-500 dark:text-gray-400">No notifications</p>
        </div>
      )}
    </motion.div>
  )
}

export default NotificationsPage
