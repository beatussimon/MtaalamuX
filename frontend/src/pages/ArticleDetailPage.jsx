import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Star, Eye, Calendar, User, MessageSquare, Share2 } from 'lucide-react'
import { articleService } from '../services/api'
import { useAuthStore } from '../store'

function ArticleDetailPage() {
  const { id } = useParams()
  const { isAuthenticated } = useAuthStore()
  const [article, setArticle] = useState(null)
  const [comments, setComments] = useState([])
  const [loading, setLoading] = useState(true)
  const [newComment, setNewComment] = useState('')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [articleRes, commentsRes] = await Promise.all([
          articleService.getById(id),
          articleService.getComments(id),
        ])
        setArticle(articleRes.data)
        setComments(commentsRes.data.results || commentsRes.data)
      } catch (error) {
        console.error('Failed to fetch article:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [id])

  const handleLike = async () => {
    if (!isAuthenticated) return
    try {
      await articleService.like(id)
      setArticle({ ...article, like_count: (article.like_count || 0) + 1, is_liked: true })
    } catch (error) {
      console.error('Failed to like:', error)
    }
  }

  const handleComment = async (e) => {
    e.preventDefault()
    if (!newComment.trim()) return
    try {
      await articleService.createComment(id, { content: newComment })
      setNewComment('')
      // Refresh comments
      const commentsRes = await articleService.getComments(id)
      setComments(commentsRes.data.results || commentsRes.data)
    } catch (error) {
      console.error('Failed to comment:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
      </div>
    )
  }

  if (!article) {
    return <div className="text-center py-12">Article not found</div>
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-4xl mx-auto">
      <article>
        {article.image && (
          <div className="h-64 md:h-96 rounded-2xl overflow-hidden mb-8">
            <img src={article.image} alt={article.title} className="w-full h-full object-cover" />
          </div>
        )}
        
        <div className="flex items-center space-x-4 mb-4">
          <span className="badge-primary">{article.category?.name}</span>
          <span className="text-sm text-gray-500">
            {new Date(article.publish_date).toLocaleDateString()}
          </span>
        </div>
        
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-6">
          {article.title}
        </h1>
        
        <div className="flex items-center justify-between py-4 border-y border-gray-200 dark:border-dark-700">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full overflow-hidden">
              {article.author?.photo ? (
                <img src={article.author.photo} alt={article.author?.user?.username} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                  <span className="text-primary-600 dark:text-primary-400 font-medium">
                    {article.author?.user?.username?.charAt(0).toUpperCase()}
                  </span>
                </div>
              )}
            </div>
            <div>
              <p className="font-medium text-gray-900 dark:text-white">{article.author?.user?.username}</p>
              <p className="text-sm text-gray-500">{article.author?.field?.name}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <button onClick={handleLike} className={`flex items-center space-x-1 ${article.is_liked ? 'text-primary-600' : 'text-gray-500'}`}>
              <Star className={`w-5 h-5 ${article.is_liked ? 'fill-current' : ''}`} />
              <span>{article.like_count || 0}</span>
            </button>
            <button className="flex items-center space-x-1 text-gray-500">
              <Eye className="w-5 h-5" />
              <span>{article.views || 0}</span>
            </button>
            <button className="flex items-center space-x-1 text-gray-500">
              <Share2 className="w-5 h-5" />
              <span>{article.shares || 0}</span>
            </button>
          </div>
        </div>
        
        <div className="prose dark:prose-invert max-w-none mt-8" dangerouslySetInnerHTML={{ __html: article.content }} />
      </article>
      
      <section className="mt-12">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
          <MessageSquare className="w-6 h-6 mr-2" />
          Comments ({comments.length})
        </h2>
        
        {isAuthenticated && (
          <form onSubmit={handleComment} className="mb-8">
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Write a comment..."
              className="input h-24 resize-none"
            />
            <button type="submit" className="btn-primary mt-2">Post Comment</button>
          </form>
        )}
        
        <div className="space-y-6">
          {comments.map((comment) => (
            <div key={comment.id} className="card p-4">
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                  <span className="text-primary-600 dark:text-primary-400 text-sm font-medium">
                    {comment.user?.username?.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-gray-900 dark:text-white">{comment.user?.username}</span>
                    <span className="text-sm text-gray-500">{new Date(comment.created_at).toLocaleDateString()}</span>
                  </div>
                  <p className="text-gray-600 dark:text-gray-300 mt-1">{comment.content}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </motion.div>
  )
}

export default ArticleDetailPage
