import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Users, FileText, Briefcase, MessageSquare, Bell, TrendingUp } from 'lucide-react'
import { useAuthStore } from '../store'
import { Link } from 'react-router-dom'

function DashboardPage() {
  const { user } = useAuthStore()
  const [stats, setStats] = useState({
    followers: 0,
    articles: 0,
    messages: 0,
    notifications: 0,
  })

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Welcome back, {user?.username}!
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Here's what's happening with your account
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { icon: Users, label: 'Followers', value: stats.followers, color: 'text-blue-500' },
          { icon: FileText, label: 'Articles', value: stats.articles, color: 'text-green-500' },
          { icon: MessageSquare, label: 'Messages', value: stats.messages, color: 'text-purple-500' },
          { icon: Bell, label: 'Notifications', value: stats.notifications, color: 'text-orange-500' },
        ].map((stat, index) => (
          <motion.div key={stat.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.1 }} className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">{stat.label}</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">{stat.value}</p>
              </div>
              <div className={`p-3 rounded-full bg-gray-100 dark:bg-dark-700 ${stat.color}`}>
                <stat.icon className="w-6 h-6" />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-4">
            <Link to="/profile" className="p-4 rounded-lg bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600 transition-colors">
              <FileText className="w-6 h-6 text-primary-600 mb-2" />
              <p className="font-medium text-gray-900 dark:text-white">Edit Profile</p>
            </Link>
            <Link to="/articles" className="p-4 rounded-lg bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600 transition-colors">
              <TrendingUp className="w-6 h-6 text-green-500 mb-2" />
              <p className="font-medium text-gray-900 dark:text-white">Write Article</p>
            </Link>
            <Link to="/jobs" className="p-4 rounded-lg bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600 transition-colors">
              <Briefcase className="w-6 h-6 text-purple-500 mb-2" />
              <p className="font-medium text-gray-900 dark:text-white">Browse Jobs</p>
            </Link>
            <Link to="/messages" className="p-4 rounded-lg bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600 transition-colors">
              <MessageSquare className="w-6 h-6 text-orange-500 mb-2" />
              <p className="font-medium text-gray-900 dark:text-white">Messages</p>
            </Link>
          </div>
        </div>

        <div className="card p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Recent Activity</h2>
          <div className="space-y-4">
            <p className="text-gray-500 dark:text-gray-400 text-center py-8">No recent activity</p>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default DashboardPage
