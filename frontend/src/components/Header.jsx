import { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Sun,
  Moon,
  Menu,
  Bell,
  MessageSquare,
  User,
  LogOut,
  LayoutDashboard,
  Settings,
  Crown,
  Zap,
  Shield
} from 'lucide-react'
import { useAuthStore, useThemeStore, useUIStore, tierHelpers } from '../store'
import { notificationService } from '../services/api'

function Header() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, isAuthenticated, logout, tierInfo } = useAuthStore()
  const { theme, toggleTheme } = useThemeStore()
  const { openSidebar } = useUIStore()
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)

  useEffect(() => {
    if (isAuthenticated) {
      fetchNotifications()
    }
  }, [isAuthenticated])

  const fetchNotifications = async () => {
    try {
      const response = await notificationService.getUnread()
      setNotifications(response.data)
      setUnreadCount(response.data.length)
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/')
    setShowUserMenu(false)
  }

  const upgradeCTA = tierHelpers.getUpgradeCTA(tierInfo)
  const displayTier = tierHelpers.getDisplayTier(tierInfo)
  const isPremium = tierHelpers.isPremium(tierInfo)
  const isProfessional = tierHelpers.isProfessional(tierInfo)

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'Professionals', path: '/professionals' },
    { name: 'Articles', path: '/articles' },
    { name: 'Research', path: '/research' },
    { name: 'Jobs', path: '/jobs' },
    { name: 'FAQ', path: '/faq' },
  ]

  return (
    <header className="sticky top-0 z-50 bg-white/80 dark:bg-dark-900/80 backdrop-blur-lg border-b border-gray-200 dark:border-dark-700">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-xl">M</span>
            </div>
            <span className="text-xl font-bold text-gray-900 dark:text-white hidden sm:block">
              MtaalamuX
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                to={link.path}
                className={`text-sm font-medium transition-colors duration-200 ${
                  location.pathname === link.path
                    ? 'text-primary-600 dark:text-primary-400'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                {link.name}
              </Link>
            ))}
          </nav>

          {/* Right side */}
          <div className="flex items-center space-x-4">
            {/* Theme toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-800 transition-colors"
              aria-label="Toggle theme"
            >
              {theme === 'light' ? (
                <Moon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              ) : (
                <Sun className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              )}
            </button>

            {isAuthenticated ? (
              <>
                {/* Tier indicator / Upgrade CTA */}
                {upgradeCTA && (
                  <Link
                    to="/upgrade"
                    className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      upgradeCTA === 'Premium'
                        ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
                        : 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400'
                    }`}
                  >
                    {upgradeCTA === 'Premium' ? (
                      <Crown className="w-4 h-4" />
                    ) : (
                      <Zap className="w-4 h-4" />
                    )}
                    <span className="hidden sm:inline">{upgradeCTA}</span>
                  </Link>
                )}

                {/* Messages */}
                <Link
                  to="/messages"
                  className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-800 transition-colors relative"
                  aria-label="Messages"
                >
                  <MessageSquare className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                </Link>

                {/* Notifications */}
                <div className="relative">
                  <button
                    onClick={() => setShowNotifications(!showNotifications)}
                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-800 transition-colors relative"
                    aria-label="Notifications"
                  >
                    <Bell className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    {unreadCount > 0 && (
                      <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                        {unreadCount}
                      </span>
                    )}
                  </button>

                  {/* Notifications dropdown */}
                  <AnimatePresence>
                    {showNotifications && (
                      <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="absolute right-0 mt-2 w-80 bg-white dark:bg-dark-800 rounded-xl shadow-lg border border-gray-200 dark:border-dark-700 overflow-hidden"
                      >
                        <div className="p-4 border-b border-gray-200 dark:border-dark-700">
                          <h3 className="font-semibold text-gray-900 dark:text-white">
                            Notifications
                          </h3>
                        </div>
                        <div className="max-h-64 overflow-y-auto">
                          {notifications.length > 0 ? (
                            notifications.map((notification) => (
                              <div
                                key={notification.id}
                                className="p-4 border-b border-gray-100 dark:border-dark-700 hover:bg-gray-50 dark:hover:bg-dark-700 cursor-pointer"
                                onClick={() => {
                                  navigate(notification.link || '/notifications')
                                  setShowNotifications(false)
                                }}
                              >
                                <p className="text-sm text-gray-900 dark:text-white">
                                  {notification.message}
                                </p>
                                <p className="text-xs text-gray-500 mt-1">
                                  {new Date(notification.created_at).toLocaleDateString()}
                                </p>
                              </div>
                            ))
                          ) : (
                            <div className="p-4 text-center text-gray-500">
                              No new notifications
                            </div>
                          )}
                        </div>
                        <Link
                          to="/notifications"
                          className="block p-3 text-center text-sm text-primary-600 dark:text-primary-400 hover:bg-gray-50 dark:hover:bg-dark-700"
                          onClick={() => setShowNotifications(false)}
                        >
                          View all notifications
                        </Link>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                {/* User menu */}
                <div className="relative">
                  <button
                    onClick={() => setShowUserMenu(!showUserMenu)}
                    className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-800 transition-colors"
                  >
                    <div className="w-8 h-8 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                      {user?.photo ? (
                        <img
                          src={user.photo}
                          alt={user.username}
                          className="w-8 h-8 rounded-full object-cover"
                        />
                      ) : (
                        <User className="w-4 h-4 text-primary-600 dark:text-primary-400" />
                      )}
                    </div>
                    <span className="hidden sm:block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {user?.username}
                    </span>
                    {displayTier && (
                      <span className={`hidden sm:inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                        isPremium
                          ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
                          : isProfessional
                          ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                      }`}>
                        {isPremium && <Shield className="w-3 h-3 mr-1" />}
                        {displayTier}
                      </span>
                    )}
                  </button>

                  {/* User dropdown */}
                  <AnimatePresence>
                    {showUserMenu && (
                      <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="absolute right-0 mt-2 w-56 bg-white dark:bg-dark-800 rounded-xl shadow-lg border border-gray-200 dark:border-dark-700 overflow-hidden"
                      >
                        <div className="px-4 py-3 border-b border-gray-200 dark:border-dark-700">
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {user?.username}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {user?.email}
                          </p>
                          {tierInfo && (
                            <span className={`inline-flex items-center mt-2 px-2 py-0.5 rounded text-xs font-medium ${
                              isPremium
                                ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
                                : isProfessional
                                ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                                : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                            }`}>
                              {displayTier} Tier
                            </span>
                          )}
                        </div>
                        <Link
                          to="/dashboard"
                          className="flex items-center space-x-2 px-4 py-3 hover:bg-gray-50 dark:hover:bg-dark-700 transition-colors"
                          onClick={() => setShowUserMenu(false)}
                        >
                          <LayoutDashboard className="w-4 h-4 text-gray-500" />
                          <span className="text-sm text-gray-700 dark:text-gray-300">Dashboard</span>
                        </Link>
                        <Link
                          to="/profile"
                          className="flex items-center space-x-2 px-4 py-3 hover:bg-gray-50 dark:hover:bg-dark-700 transition-colors"
                          onClick={() => setShowUserMenu(false)}
                        >
                          <User className="w-4 h-4 text-gray-500" />
                          <span className="text-sm text-gray-700 dark:text-gray-300">Profile</span>
                        </Link>
                        <Link
                          to="/messages"
                          className="flex items-center space-x-2 px-4 py-3 hover:bg-gray-50 dark:hover:bg-dark-700 transition-colors"
                          onClick={() => setShowUserMenu(false)}
                        >
                          <MessageSquare className="w-4 h-4 text-gray-500" />
                          <span className="text-sm text-gray-700 dark:text-gray-300">Messages</span>
                        </Link>
                        <Link
                          to="/settings"
                          className="flex items-center space-x-2 px-4 py-3 hover:bg-gray-50 dark:hover:bg-dark-700 transition-colors"
                          onClick={() => setShowUserMenu(false)}
                        >
                          <Settings className="w-4 h-4 text-gray-500" />
                          <span className="text-sm text-gray-700 dark:text-gray-300">Settings</span>
                        </Link>
                        {upgradeCTA && (
                          <Link
                            to="/upgrade"
                            className="flex items-center space-x-2 px-4 py-3 hover:bg-gray-50 dark:hover:bg-dark-700 transition-colors text-primary-600 dark:text-primary-400"
                            onClick={() => setShowUserMenu(false)}
                          >
                            <Crown className="w-4 h-4" />
                            <span className="text-sm font-medium">{upgradeCTA} to Premium</span>
                          </Link>
                        )}
                        <hr className="border-gray-200 dark:border-dark-700" />
                        <button
                          onClick={handleLogout}
                          className="flex items-center space-x-2 px-4 py-3 w-full hover:bg-gray-50 dark:hover:bg-dark-700 transition-colors text-left"
                        >
                          <LogOut className="w-4 h-4 text-red-500" />
                          <span className="text-sm text-red-600 dark:text-red-400">Logout</span>
                        </button>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </>
            ) : (
              <div className="flex items-center space-x-2">
                <Link to="/login" className="btn-ghost text-sm">
                  Login
                </Link>
                <Link to="/register" className="btn-primary text-sm">
                  Sign Up
                </Link>
              </div>
            )}

            {/* Mobile menu button */}
            <button
              onClick={openSidebar}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-800 transition-colors lg:hidden"
              aria-label="Menu"
            >
              <Menu className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
