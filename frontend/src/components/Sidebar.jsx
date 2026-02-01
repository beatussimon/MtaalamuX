import { Link, useLocation } from 'react-router-dom'
import { X, Home, Users, FileText, Briefcase, MessageSquare, Bell, Settings, User, LogOut } from 'lucide-react'
import { useAuthStore, useUIStore } from '../store'

function Sidebar() {
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const { closeSidebar } = useUIStore()

  const menuItems = [
    { icon: Home, label: 'Dashboard', path: '/dashboard' },
    { icon: User, label: 'My Profile', path: '/profile' },
    { icon: Users, label: 'Professionals', path: '/professionals' },
    { icon: FileText, label: 'Articles', path: '/articles' },
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
      <div className="p-4 border-b border-gray-200 dark:border-dark-700">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
            <User className="w-5 h-5 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <p className="font-medium text-gray-900 dark:text-white">{user?.username}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">{user?.email}</p>
          </div>
        </div>
      </div>

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
