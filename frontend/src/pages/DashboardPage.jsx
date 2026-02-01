import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Users,
  FileText,
  Briefcase,
  MessageSquare,
  Bell,
  TrendingUp,
  Crown,
  Zap,
  Shield,
  BookOpen,
  ShoppingCart,
  BarChart3,
  DollarSign,
  Star,
  Heart,
  Eye,
  User
} from 'lucide-react'
import { useAuthStore, tierHelpers } from '../store'
import { Link } from 'react-router-dom'
import { consultationService, consultationTaskService, articleService } from '../services/api'

function DashboardPage() {
  const { user, tierInfo } = useAuthStore()
  const [stats, setStats] = useState({
    followers: 0,
    articles: 0,
    messages: 0,
    notifications: 0,
    consultations: 0,
    earnings: 0,
    tasks: 0,
    research: 0,
    digitalSales: 0,
    merchSales: 0,
  })
  const [loading, setLoading] = useState(true)
  const [recentConsultations, setRecentConsultations] = useState([])
  const [myTasks, setMyTasks] = useState([])

  const isBasic = tierHelpers.isBasic(tierInfo)
  const isProfessional = tierHelpers.isProfessional(tierInfo)
  const isPremium = tierHelpers.isPremium(tierInfo)
  const canInitiateConsultation = tierHelpers.canInitiateConsultation(tierInfo)
  const canPostContent = tierHelpers.canPostContent(tierInfo)
  const canSellItems = tierHelpers.canSellItems(tierInfo)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch consultations if user is authenticated
        if (isProfessional || isPremium) {
          const [consultationsRes, tasksRes] = await Promise.all([
            consultationService.getMyConsultations(),
            consultationTaskService.getMyTasks(),
          ])
          setRecentConsultations(consultationsRes.data.results || consultationsRes.data)
          setMyTasks(tasksRes.data.results || tasksRes.data)
        }

        // Simulated stats (would come from API in production)
        setStats({
          followers: user?.follower_count || 0,
          articles: user?.article_count || 0,
          messages: user?.message_count || 0,
          notifications: user?.notification_count || 0,
          consultations: user?.consultation_count || 0,
          earnings: user?.earnings || 0,
          tasks: myTasks.length,
          research: user?.research_count || 0,
          digitalSales: user?.digital_sales || 0,
          merchSales: user?.merch_sales || 0,
        })
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [user, isProfessional, isPremium])

  const getTierColor = () => {
    if (isPremium) return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
    if (isProfessional) return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
    return 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
  }

  const getTierIcon = () => {
    if (isPremium) return <Crown className="w-5 h-5" />
    if (isProfessional) return <Zap className="w-5 h-5" />
    return <Shield className="w-5 h-5" />
  }

  const getTierName = () => {
    if (isPremium) return 'Premium Expert'
    if (isProfessional) return 'Professional'
    return 'Basic'
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      {/* Header with tier info */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Welcome back, {user?.username}!
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Here's what's happening with your account
          </p>
        </div>
        <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${getTierColor()}`}>
          {getTierIcon()}
          <span className="font-medium">{getTierName()} Account</span>
        </div>
      </div>

      {/* Upgrade prompt for Basic users */}
      {isBasic && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-6 bg-gradient-to-r from-primary-500 to-primary-700 rounded-xl"
        >
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white mb-2">
                Unlock Full Access
              </h2>
              <p className="text-primary-100">
                Upgrade to Professional to initiate consultations, message experts, and apply for jobs.
              </p>
            </div>
            <Link
              to="/upgrade"
              className="btn bg-white text-primary-600 hover:bg-primary-50 px-6 py-3 flex-shrink-0"
            >
              Upgrade Now
            </Link>
          </div>
        </motion.div>
      )}

      {/* Professional upgrade prompt */}
      {isProfessional && !isPremium && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-6 bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-xl"
        >
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                <Crown className="w-6 h-6" />
                Become a Premium Expert
              </h2>
              <p className="text-yellow-100">
                Get verified, appear in Top Experts, sell digital items and merch, and access premium features.
              </p>
            </div>
            <Link
              to="/upgrade"
              className="btn bg-white text-yellow-600 hover:bg-yellow-50 px-6 py-3 flex-shrink-0"
            >
              Go Premium
            </Link>
          </div>
        </motion.div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {/* Always visible stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card p-4"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Followers</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.followers}</p>
            </div>
            <div className="p-2 rounded-full bg-blue-100 dark:bg-blue-900/30">
              <Users className="w-5 h-5 text-blue-500" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card p-4"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Articles</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.articles}</p>
            </div>
            <div className="p-2 rounded-full bg-green-100 dark:bg-green-900/30">
              <FileText className="w-5 h-5 text-green-500" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card p-4"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Messages</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.messages}</p>
            </div>
            <div className="p-2 rounded-full bg-purple-100 dark:bg-purple-900/30">
              <MessageSquare className="w-5 h-5 text-purple-500" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card p-4"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Notifications</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.notifications}</p>
            </div>
            <div className="p-2 rounded-full bg-orange-100 dark:bg-orange-900/30">
              <Bell className="w-5 h-5 text-orange-500" />
            </div>
          </div>
        </motion.div>

        {/* Professional/Premium stats */}
        {(isProfessional || isPremium) && (
          <>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="card p-4"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Consultations</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.consultations}</p>
                </div>
                <div className="p-2 rounded-full bg-teal-100 dark:bg-teal-900/30">
                  <TrendingUp className="w-5 h-5 text-teal-500" />
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="card p-4"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Tasks</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.tasks}</p>
                </div>
                <div className="p-2 rounded-full bg-indigo-100 dark:bg-indigo-900/30">
                  <Briefcase className="w-5 h-5 text-indigo-500" />
                </div>
              </div>
            </motion.div>
          </>
        )}

        {/* Premium only stats */}
        {isPremium && (
          <>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
              className="card p-4"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Research</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.research}</p>
                </div>
                <div className="p-2 rounded-full bg-cyan-100 dark:bg-cyan-900/30">
                  <BookOpen className="w-5 h-5 text-cyan-500" />
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="card p-4"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Earnings</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">${stats.earnings}</p>
                </div>
                <div className="p-2 rounded-full bg-yellow-100 dark:bg-yellow-900/30">
                  <DollarSign className="w-5 h-5 text-yellow-500" />
                </div>
              </div>
            </motion.div>
          </>
        )}
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Actions - changes based on tier */}
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-4">
            {/* Available to all authenticated users */}
            <Link to="/profile" className="p-4 rounded-lg bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600 transition-colors">
              <User className="w-6 h-6 text-primary-600 mb-2" />
              <p className="font-medium text-gray-900 dark:text-white">Edit Profile</p>
            </Link>

            <Link to="/messages" className="p-4 rounded-lg bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600 transition-colors">
              <MessageSquare className="w-6 h-6 text-purple-500 mb-2" />
              <p className="font-medium text-gray-900 dark:text-white">Messages</p>
            </Link>

            {/* Professional/Premium actions */}
            {(isProfessional || isPremium) && (
              <>
                <Link to="/consultations" className="p-4 rounded-lg bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600 transition-colors">
                  <TrendingUp className="w-6 h-6 text-teal-500 mb-2" />
                  <p className="font-medium text-gray-900 dark:text-white">My Consultations</p>
                </Link>

                <Link to="/tasks" className="p-4 rounded-lg bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600 transition-colors">
                  <Briefcase className="w-6 h-6 text-indigo-500 mb-2" />
                  <p className="font-medium text-gray-900 dark:text-white">Tasks</p>
                </Link>
              </>
            )}

            {/* Premium only actions */}
            {isPremium && (
              <>
                <Link to="/articles/new" className="p-4 rounded-lg bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600 transition-colors">
                  <FileText className="w-6 h-6 text-green-500 mb-2" />
                  <p className="font-medium text-gray-900 dark:text-white">Write Article</p>
                </Link>

                <Link to="/research/new" className="p-4 rounded-lg bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600 transition-colors">
                  <BookOpen className="w-6 h-6 text-cyan-500 mb-2" />
                  <p className="font-medium text-gray-900 dark:text-white">Publish Research</p>
                </Link>

                <Link to="/digital-items/new" className="p-4 rounded-lg bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600 transition-colors">
                  <ShoppingCart className="w-6 h-6 text-yellow-500 mb-2" />
                  <p className="font-medium text-gray-900 dark:text-white">Sell Digital Item</p>
                </Link>

                <Link to="/merch/new" className="p-4 rounded-lg bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600 transition-colors">
                  <ShoppingCart className="w-6 h-6 text-pink-500 mb-2" />
                  <p className="font-medium text-gray-900 dark:text-white">Add Merch</p>
                </Link>
              </>
            )}

            {/* Upgrade CTA for Basic */}
            {isBasic && (
              <Link to="/upgrade" className="p-4 rounded-lg bg-primary-50 dark:bg-primary-900/30 hover:bg-primary-100 dark:hover:bg-primary-900/50 transition-colors">
                <Crown className="w-6 h-6 text-primary-600 mb-2" />
                <p className="font-medium text-primary-700 dark:text-primary-400">Upgrade to Professional</p>
              </Link>
            )}
          </div>
        </div>

        {/* Recent Activity / Consultations */}
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            {isPremium ? 'Recent Consultations' : 'Recent Activity'}
          </h2>
          <div className="space-y-4">
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
                <p className="text-gray-500 mt-2">Loading...</p>
              </div>
            ) : recentConsultations.length > 0 ? (
              recentConsultations.slice(0, 3).map((consultation) => (
                <div key={consultation.id} className="p-4 rounded-lg bg-gray-50 dark:bg-dark-700">
                  <div className="flex items-center justify-between mb-2">
                    <p className="font-medium text-gray-900 dark:text-white">
                      {consultation.subject}
                    </p>
                    <span className={`badge ${
                      consultation.status === 'completed' ? 'badge-success' :
                      consultation.status === 'in_progress' ? 'badge-warning' :
                      'badge-primary'
                    }`}>
                      {consultation.status?.replace('_', ' ')}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {consultation.client?.username || consultation.expert?.username}
                  </p>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                    {new Date(consultation.created_at).toLocaleDateString()}
                  </p>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <MessageSquare className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                <p className="text-gray-500 dark:text-gray-400">
                  {isBasic ? 'No recent activity' : 'No consultations yet'}
                </p>
                {(isProfessional || isPremium) && (
                  <Link to="/professionals" className="text-primary-600 dark:text-primary-400 text-sm mt-2 inline-block">
                    Browse experts to start a consultation
                  </Link>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Premium Analytics Dashboard */}
      {isPremium && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <BarChart3 className="w-6 h-6 text-primary-600" />
              Expert Analytics
            </h2>
            <Link to="/analytics" className="text-primary-600 dark:text-primary-400 text-sm">
              View Full Analytics
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 rounded-lg bg-gray-50 dark:bg-dark-700">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-500 dark:text-gray-400">Consultation Rate</span>
                <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
              </div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">4.8</p>
              <p className="text-xs text-gray-400 dark:text-gray-500">Based on 24 ratings</p>
            </div>
            <div className="p-4 rounded-lg bg-gray-50 dark:bg-dark-700">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-500 dark:text-gray-400">Response Time</span>
                <TrendingUp className="w-4 h-4 text-green-500" />
              </div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">2.5h</p>
              <p className="text-xs text-gray-400 dark:text-gray-500">Average response</p>
            </div>
            <div className="p-4 rounded-lg bg-gray-50 dark:bg-dark-700">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-500 dark:text-gray-400">Monthly Views</span>
                <Eye className="w-4 h-4 text-blue-500" />
              </div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">1.2K</p>
              <p className="text-xs text-gray-400 dark:text-gray-500">Profile views this month</p>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}

export default DashboardPage
