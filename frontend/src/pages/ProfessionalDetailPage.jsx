import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Star, MapPin, Users, Award, MessageSquare } from 'lucide-react'
import { professionalService } from '../services/api'
import { useAuthStore } from '../store'

function ProfessionalDetailPage() {
  const { id } = useParams()
  const { isAuthenticated } = useAuthStore()
  const [professional, setProfessional] = useState(null)
  const [articles, setArticles] = useState([])
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [isFollowing, setIsFollowing] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [profRes, articlesRes, reviewsRes] = await Promise.all([
          professionalService.getById(id),
          professionalService.getArticles(id),
          professionalService.getReviews(id),
        ])
        setProfessional(profRes.data)
        setArticles(articlesRes.data.results || articlesRes.data)
        setReviews(reviewsRes.data.results || reviewsRes.data)
      } catch (error) {
        console.error('Failed to fetch professional:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [id])

  const handleFollow = async () => {
    if (!isAuthenticated) {
      // Redirect to login
      return
    }
    try {
      await professionalService.follow(id)
      setIsFollowing(!isFollowing)
    } catch (error) {
      console.error('Failed to follow:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
      </div>
    )
  }

  if (!professional) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 dark:text-gray-400">Professional not found</p>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-8"
    >
      {/* Header */}
      <div className="card overflow-hidden">
        <div className="h-48 bg-gradient-to-r from-primary-600 to-primary-800" />
        <div className="px-8 pb-8">
          <div className="flex flex-col md:flex-row md:items-end md:space-x-6 -mt-16">
            <div className="w-32 h-32 rounded-2xl overflow-hidden ring-4 ring-white dark:ring-dark-800">
              {professional.photo ? (
                <img
                  src={professional.photo}
                  alt={professional.user?.username}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                  <span className="text-4xl font-bold text-primary-600 dark:text-primary-400">
                    {professional.user?.username?.charAt(0).toUpperCase()}
                  </span>
                </div>
              )}
            </div>
            <div className="flex-1 mt-4 md:mt-0 md:mb-2">
              <div className="flex items-center space-x-2">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {professional.user?.username}
                </h1>
                {professional.is_verified && (
                  <Award className="w-5 h-5 text-primary-600" />
                )}
              </div>
              <p className="text-gray-500 dark:text-gray-400">
                {professional.field?.name} {professional.subfield && `• ${professional.subfield}`}
              </p>
              {professional.location && (
                <div className="flex items-center space-x-1 mt-1 text-sm text-gray-500">
                  <MapPin className="w-4 h-4" />
                  <span>{professional.location}</span>
                </div>
              )}
            </div>
            <div className="flex space-x-3 mt-4 md:mt-0 md:mb-2">
              <button
                onClick={handleFollow}
                className={`btn ${isFollowing ? 'btn-secondary' : 'btn-primary'}`}
              >
                <Users className="w-4 h-4 mr-2" />
                {isFollowing ? 'Following' : 'Follow'}
              </button>
              <button className="btn-outline">
                <MessageSquare className="w-4 h-4 mr-2" />
                Message
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card p-4 text-center">
          <Star className="w-6 h-6 mx-auto mb-2 text-yellow-500" />
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            {professional.avg_rating?.toFixed(1) || '0.0'}
          </p>
          <p className="text-sm text-gray-500">Rating</p>
        </div>
        <div className="card p-4 text-center">
          <Users className="w-6 h-6 mx-auto mb-2 text-primary-500" />
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            {professional.followers_count || 0}
          </p>
          <p className="text-sm text-gray-500">Followers</p>
        </div>
        <div className="card p-4 text-center">
          <Award className="w-6 h-6 mx-auto mb-2 text-green-500" />
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            {professional.article_count || 0}
          </p>
          <p className="text-sm text-gray-500">Articles</p>
        </div>
        <div className="card p-4 text-center">
          <MessageSquare className="w-6 h-6 mx-auto mb-2 text-purple-500" />
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            {reviews.length}
          </p>
          <p className="text-sm text-gray-500">Reviews</p>
        </div>
      </div>

      {/* Bio */}
      {professional.bio && (
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            About
          </h2>
          <p className="text-gray-600 dark:text-gray-300 whitespace-pre-wrap">
            {professional.bio}
          </p>
        </div>
      )}

      {/* Articles */}
      {articles.length > 0 && (
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Recent Articles
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {articles.slice(0, 4).map((article) => (
              <div key={article.id} className="border border-gray-200 dark:border-dark-700 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 dark:text-white hover:text-primary-600 cursor-pointer">
                  {article.title}
                </h3>
                <p className="text-sm text-gray-500 mt-1">
                  {new Date(article.publish_date).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Reviews */}
      {reviews.length > 0 && (
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Reviews
          </h2>
          <div className="space-y-4">
            {reviews.map((review) => (
              <div key={review.id} className="border-b border-gray-100 dark:border-dark-700 pb-4 last:border-0">
                <div className="flex items-center justify-between">
                  <p className="font-medium text-gray-900 dark:text-white">
                    {review.reviewer?.username}
                  </p>
                  <div className="flex items-center space-x-1">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-4 h-4 ${
                          i < review.rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                </div>
                <p className="text-gray-600 dark:text-gray-300 mt-2">{review.comment}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  )
}

export default ProfessionalDetailPage
