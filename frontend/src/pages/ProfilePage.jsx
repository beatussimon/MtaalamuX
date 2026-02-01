import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  User, Mail, Camera, Save, Shield, Crown, Zap, 
  MapPin, Phone, Calendar, Edit2, Shield as ShieldIcon
} from 'lucide-react'
import { useAuthStore, useThemeStore, tierHelpers } from '../store'
import { userService } from '../services/api'
import toast from 'react-hot-toast'

function ProfilePage() {
  const navigate = useNavigate()
  const { user, tierInfo } = useAuthStore()
  const { setTheme } = useThemeStore()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    bio: '',
    interests: '',
    theme: 'light',
    location: '',
    phone: '',
  })

  const isBasic = tierHelpers.isBasic(tierInfo)
  const isProfessional = tierHelpers.isProfessional(tierInfo)
  const isPremium = tierHelpers.isPremium(tierInfo)
  const displayTier = tierHelpers.getDisplayTier(tierInfo)

  useEffect(() => {
    if (user) {
      setFormData({
        bio: user.profile?.bio || '',
        interests: user.profile?.interests || '',
        theme: user.profile?.theme || 'light',
        location: user.profile?.location || '',
        phone: user.profile?.phone || '',
      })
    }
  }, [user])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    
    if (name === 'theme') {
      setTheme(value)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await userService.updateProfile(formData)
      toast.success('Profile updated successfully')
      setIsEditing(false)
    } catch (error) {
      console.error('Failed to update profile:', error)
      toast.error(error.response?.data?.detail || 'Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  if (!user) {
    return (
      <motion.div 
        initial={{ opacity: 0 }} 
        animate={{ opacity: 1 }} 
        className="flex flex-col items-center justify-center h-[calc(100vh-12rem)]"
      >
        <div className="w-20 h-20 bg-gray-100 dark:bg-dark-800 rounded-full flex items-center justify-center mb-6">
          <User className="w-10 h-10 text-gray-400" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Please Sign In
        </h2>
        <p className="text-gray-500 dark:text-gray-400 text-center max-w-md mb-6">
          Sign in to view and edit your profile
        </p>
        <button onClick={() => navigate('/login')} className="btn-primary">
          Sign In
        </button>
      </motion.div>
    )
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-4xl mx-auto space-y-8">
      {/* Profile Header */}
      <div className="card p-6">
        <div className="flex flex-col md:flex-row items-start gap-6">
          {/* Avatar */}
          <div className="relative">
            <div className="w-32 h-32 rounded-full overflow-hidden ring-4 ring-primary-100 dark:ring-primary-900">
              {user.photo ? (
                <img 
                  src={user.photo} 
                  alt={user.username} 
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                  <User className="w-16 h-16 text-primary-600 dark:text-primary-400" />
                </div>
              )}
            </div>
            <button className="absolute bottom-0 right-0 p-2 bg-primary-600 text-white rounded-full hover:bg-primary-700 transition-colors shadow-lg">
              <Camera className="w-4 h-4" />
            </button>
          </div>

          {/* User Info */}
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                {user.username}
              </h1>
              {tierInfo && (
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  isPremium
                    ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
                    : isProfessional
                      ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                }`}>
                  {isPremium && <Crown className="w-4 h-4 mr-1" />}
                  {isProfessional && <Zap className="w-4 h-4 mr-1" />}
                  {!isPremium && !isProfessional && <ShieldIcon className="w-4 h-4 mr-1" />}
                  {displayTier}
                </span>
              )}
            </div>
            
            <div className="flex items-center gap-4 text-gray-500 dark:text-gray-400 text-sm mb-4">
              <span className="flex items-center gap-1">
                <Mail className="w-4 h-4" />
                {user.email}
              </span>
              {formData.location && (
                <span className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  {formData.location}
                </span>
              )}
              <span className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                Joined {new Date(user.date_joined).toLocaleDateString()}
              </span>
            </div>

            <div className="flex items-center gap-4">
              <button 
                onClick={() => setIsEditing(!isEditing)}
                className="btn-outline flex items-center gap-2"
              >
                <Edit2 className="w-4 h-4" />
                {isEditing ? 'Cancel' : 'Edit Profile'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Profile Form */}
      <form onSubmit={handleSubmit} className="card p-6 space-y-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Profile Information
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Bio
            </label>
            <textarea
              name="bio"
              value={formData.bio}
              onChange={handleChange}
              disabled={!isEditing}
              className="input h-32 resize-none"
              placeholder="Tell us about yourself..."
            />
          </div>

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Location
              </label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleChange}
                  disabled={!isEditing}
                  className="input pl-10"
                  placeholder="City, Country"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Phone Number
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  disabled={!isEditing}
                  className="input pl-10"
                  placeholder="+254 700 000 000"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Theme
              </label>
              <select
                name="theme"
                value={formData.theme}
                onChange={handleChange}
                disabled={!isEditing}
                className="input"
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
              </select>
            </div>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Interests
          </label>
          <input
            type="text"
            name="interests"
            value={formData.interests}
            onChange={handleChange}
            disabled={!isEditing}
            className="input"
            placeholder="e.g., Programming, Design, Writing (comma separated)"
          />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Enter your interests separated by commas
          </p>
        </div>

        {isEditing && (
          <div className="flex justify-end gap-4 pt-4 border-t border-gray-200 dark:border-dark-700">
            <button
              type="button"
              onClick={() => setIsEditing(false)}
              className="btn-outline"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="btn-primary flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        )}
      </form>

      {/* Account Stats */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Account Stats
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg text-center">
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {user.followers_count || 0}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Followers</p>
          </div>
          <div className="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg text-center">
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {user.article_count || 0}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Articles</p>
          </div>
          <div className="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg text-center">
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {user.research_count || 0}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Research</p>
          </div>
          <div className="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg text-center">
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {user.profile?.view_count || 0}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Profile Views</p>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default ProfilePage
