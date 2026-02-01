import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Bell, Check, Trash2, MessageSquare, UserPlus, FileText, Briefcase } from 'lucide-react'
import { notificationService } from '../services/api'
import { useAuthStore } from '../store'
import { useNavigate } from 'react-router-dom'

function NotificationsPage() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuthStore()
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('all') // all, unread, read

  useEffect(() => {
    if (isAuthenticated) {
      fetchNotifications()
    }
  }, [isAuthenticated])

  const fetchNotifications = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await notificationService.getAll()
      setNotifications(response.data.results || response.data || [])
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
      setError('Failed to load notifications')
      setNotifications([])
    } finally {
      setLoading(false)
    }
  }

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

  const handleDelete = async (id) => {
    try {
      // Assuming there's a delete endpoint, otherwise just remove from state
      setNotifications(notifications.filter(n => n.id !== id))
    } catch (error) {
      console.error('Failed to delete notification:', error)
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

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'message':
      case 'new_message':
        return <MessageSquare className="w-5 h-5 text-blue-500" />
      case 'follow':
      case 'new_follower':
        return <UserPlus className="w-5 h-5 text-green-500" />
      case 'article':
      case 'new_article':
        return <FileText className="w-5 h-5 text-purple-500" />
      case 'job':
      case 'new_job':
        return <Briefcase className="w-5 h-5 text-orange-500" />
      default:
        return <Bell className="w-5 h-5 text-gray-500" />
    }
  }

  const getRelativeTime = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  const filteredNotifications = notifications.filter(n => {
    if (filter === 'unread') return !n.is_read
    if (filter === 'read') return n.is_read
    return true
  })

  const unreadCount = notifications.filter(n => !n.is_read).length

  if (!isAuthenticated) {
    return (
      <motion.div 
        initial={{ opacity: 0 }} 
        animate={{ opacity: 1 }} 
        className="max-w-3xl mx-auto text-center py-12"
      >
        <Bell className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Sign in to view notifications
        </h2>
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          You need to be logged in to see your notifications
        </p>
        <button onClick={() => navigate('/login')} className="btn-primary">
          Sign In
        </button>
      </motion.div>
    )
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
          <Bell className="w-8 h-8 mr-3" />
          Notifications
          {unreadCount > 0 && (
            <span className="ml-3 px-2 py-0.5 bg-red-500 text-white text-sm rounded-full">
              {unreadCount}
            </span>
          )}
        </h1>
        <div className="flex items-center space-x-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="input text-sm"
          >
            <option value="all">All</option>
            <option value="unread">Unread</option>
            <option value="read">Read</option>
          </select>
          {unreadCount > 0 && (
            <button onClick={handleMarkAllAsRead} className="btn-outline text-sm">
              <Check className="w-4 h-4 mr-2" />
              Mark all as read
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg">
          {error}
          <button onClick={fetchNotifications} className="ml-2 underline">
            Retry
          </button>
        </div>
      )}

      {loading ? (
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="card p-4 animate-pulse">
              <div className="flex items-start space-x-4">
                <div className="w-10 h-10 bg-gray-200 dark:bg-dark-700 rounded-full" />
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 dark:bg-dark-700 rounded w-3/4 mb-2" />
                  <div className="h-3 bg-gray-200 dark:bg-dark-700 rounded w-1/2" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : filteredNotifications.length > 0 ? (
        <div className="space-y-2">
          {filteredNotifications.map((notification, index) => (
            <motion.div
              key={notification.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              onClick={() => handleClick(notification)}
              className={`card p-4 cursor-pointer transition-all hover:shadow-md ${
                notification.is_read
                  ? 'opacity-60 hover:opacity-80'
                  : 'bg-primary-50 dark:bg-primary-900/10 border-l-4 border-primary-500'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className="flex-shrink-0 mt-1">
                    {getNotificationIcon(notification.notification_type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-gray-900 dark:text-white font-medium">
                      {notification.title || notification.message}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                      {notification.message}
                    </p>
                    <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
                      {getRelativeTime(notification.created_at)}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2 flex-shrink-0">
                  {!notification.is_read && (
                    <span className="w-2 h-2 bg-primary-500 rounded-full" />
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDelete(notification.id)
                    }}
                    className="p-1 hover:bg-gray-100 dark:hover:bg-dark-700 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Trash2 className="w-4 h-4 text-gray-400" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Bell className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
          <p className="text-gray-500 dark:text-gray-400 mb-2">
            {filter === 'unread' 
              ? 'No unread notifications' 
              : filter === 'read' 
                ? 'No read notifications' 
                : 'No notifications yet'}
          </p>
          <p className="text-sm text-gray-400 dark:text-gray-500">
            We'll notify you when something happens
          </p>
        </div>
      )}
    </motion.div>
  )
}

export default NotificationsPage
