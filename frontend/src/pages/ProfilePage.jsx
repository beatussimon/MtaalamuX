import { useState } from 'react'
import { motion } from 'framer-motion'
import { User, Mail, Camera, Save } from 'lucide-react'
import { useAuthStore } from '../store'
import { userService } from '../services/api'
import toast from 'react-hot-toast'

function ProfilePage() {
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    bio: user?.profile?.bio || '',
    interests: user?.profile?.interests || '',
    theme: user?.profile?.theme || 'light',
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await userService.updateProfile(formData)
      toast.success('Profile updated successfully')
    } catch (error) {
      toast.error('Failed to update profile')
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">Profile Settings</h1>
      
      <div className="card p-6 mb-6">
        <div className="flex items-center space-x-6">
          <div className="relative">
            <div className="w-24 h-24 rounded-full overflow-hidden">
              {user?.profile?.avatar ? (
                <img src={user.profile.avatar} alt={user.username} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                  <User className="w-12 h-12 text-primary-600 dark:text-primary-400" />
                </div>
              )}
            </div>
            <button className="absolute bottom-0 right-0 p-2 bg-primary-600 text-white rounded-full hover:bg-primary-700 transition-colors">
              <Camera className="w-4 h-4" />
            </button>
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">{user?.username}</h2>
            <p className="text-gray-500 dark:text-gray-400">{user?.email}</p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="card p-6 space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Bio</label>
          <textarea
            value={formData.bio}
            onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
            className="input h-32 resize-none"
            placeholder="Tell us about yourself..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Interests</label>
          <input
            type="text"
            value={formData.interests}
            onChange={(e) => setFormData({ ...formData, interests: e.target.value })}
            className="input"
            placeholder="e.g., Programming, Design, Writing"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Theme</label>
          <select
            value={formData.theme}
            onChange={(e) => setFormData({ ...formData, theme: e.target.value })}
            className="input"
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </div>

="submit" disabled        <button type={loading} className="btn-primary">
          <Save className="w-4 h-4 mr-2" />
          {loading ? 'Saving...' : 'Save Changes'}
        </button>
      </form>
    </motion.div>
  )
}

export default ProfilePage
