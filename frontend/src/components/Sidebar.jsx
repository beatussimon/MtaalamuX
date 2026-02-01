import { Link, useLocation } from 'react-router-dom'
import { X, Home, Users, FileText, BookOpen, Briefcase, MessageSquare, Bell, Settings, User, LogOut, Crown } from 'lucide-react'
import { useAuthStore, useUIStore, tierHelpers } from '../store'

function Sidebar() {
  const location = useLocation()
  const { user, logout, tierInfo, isAuthenticated } = useAuthStore()
  const { closeSidebar } = useUIStore()

  const isBasic = tierHelpers.isBasic(tierInfo)
  const isProfessional = tierHelpers.isProfessional(tierInfo)
  const isPremium = tierHelpers.isPremium(tierInfo)
  const upgradeCTA = tierHelpers.getUpgradeCTA(tierInfo)

  const menuItems = [
    { icon: Home, label: 'Dashboard', path: '/dashboard' },
    { icon: User, label: 'My Profile', path: '/profile' },
    { icon: Users, label: 'Professionals', path: '/professionals' },
    { icon: FileText, label: 'Articles', path: '/articles' },
    { icon: BookOpen, label: 'Research', path: '/research' },
    { icon: Briefcase, label: 'Jobs', path: '/jobs' },
    { icon: MessageSquare, label: 'Messages', path: '/messages' },
    { icon: Bell, label: 'Notifications', path: '/notifications' },
  ]

  const handleLogout = () => {
    logout()
    closeSidebar()
  }

  return (
    <div className="h-full flex flex-col">
      {/* Close button (mobile only) */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-dark-700 lg:hidden">
        <span className="font-semibold text-gray-900 dark:text-white">Menu</span>
        <button
          onClick={closeSidebar}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-700 transition-colors"
          aria-label="Close menu"
        >
          <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
        </button>
      </div>

      {/* User info */}
      {isAuthenticated && (
        <div className="p-4 border-b border-gray-200 dark:border-dark-700">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
              {user?.photo ? (
                <img src={user.photo} alt={user.username} className="w-10 h-10 rounded-full object-cover" />
              ) : (
                <User className="w-5 h-5 text-primary-600 dark:text-primary-400" />
              )}
            </div>
            <div>
              <p className="font-medium text-gray-900 dark:text-white">{user?.username}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">{user?.email}</p>
            </div>
          </div>
          {tierInfo && (
            <div className="mt-2">
              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                isPremium
                  ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
                  : isProfessional
                  ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
              }`}>
                {isPremium && <Crown className="w-3 h-3 mr-1" />}
                {tierHelpers.getDisplayTier(tierInfo)} Tier
              </span>
            </div>
          )}
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            onClick={closeSidebar}
            className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
              location.pathname === item.path
                ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400'
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-dark-700'
            }`}
          >
            <item.icon className="w-5 h-5" />
            <span className="font-medium">{item.label}</span>
          </Link>
        ))}

        {/* Upgrade CTA for basic users */}
        {isAuthenticated && upgradeCTA && (
          <Link
            to="/upgrade"
            onClick={closeSidebar}
            className="flex items-center space-x-3 px-4 py-3 rounded-lg bg-primary-50 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400"
          >
            <Crown className="w-5 h-5" />
            <span className="font-medium">{upgradeCTA} to Premium</span>
          </Link>
        )}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-dark-700 space-y-1">
        <Link
          to="/settings"
          onClick={closeSidebar}
          className="flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-dark-700 transition-colors"
        >
          <Settings className="w-5 h-5" />
          <span className="font-medium">Settings</span>
        </Link>
        <button
          onClick={handleLogout}
          className="flex items-center space-x-3 px-4 py-3 w-full rounded-lg text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span className="font-medium">Logout</span>
        </button>
      </div>
    </div>
  )
}

export default Sidebar
