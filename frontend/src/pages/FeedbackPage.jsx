import { useState } from 'react'
import { motion } from 'framer-motion'
import { Star, Send } from 'lucide-react'
import { feedbackService } from '../services/api'
import toast from 'react-hot-toast'

function FeedbackPage() {
  const [rating, setRating] = useState(0)
  const [hoverRating, setHoverRating] = useState(0)
  const [message, setMessage] = useState('')
  const [category, setCategory] = useState('general')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!message.trim()) {
      toast.error('Please enter your feedback')
      return
    }
    
    setSubmitting(true)
    try {
      await feedbackService.create({
        message,
        rating: rating || null,
        category,
      })
      toast.success('Thank you for your feedback!')
      setMessage('')
      setRating(0)
      setCategory('general')
    } catch (error) {
      toast.error('Failed to submit feedback')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Send Us Feedback</h1>
        <p className="text-gray-500 dark:text-gray-400">We'd love to hear from you. Your feedback helps us improve.</p>
      </div>

      <form onSubmit={handleSubmit} className="card p-8 space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Category</label>
          <select value={category} onChange={(e) => setCategory(e.target.value)} className="input">
            <option value="general">General</option>
            <option value="bug">Bug Report</option>
            <option value="feature">Feature Request</option>
            <option value="content">Content Feedback</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Rating (Optional)</label>
          <div className="flex space-x-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                onClick={() => setRating(star)}
                onMouseEnter={() => setHoverRating(star)}
                onMouseLeave={() => setHoverRating(0)}
                className="p-1 transition-transform hover:scale-110"
              >
                <Star
                  className={`w-8 h-8 ${
                    star <= (hoverRating || rating)
                      ? 'text-yellow-400 fill-yellow-400'
                      : 'text-gray-300 dark:text-gray-600'
                  }`}
                />
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Your Feedback</label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="input h-40 resize-none"
            placeholder="Tell us what you think..."
            required
          />
        </div>

        <button type="submit" disabled={submitting} className="btn-primary w-full py-3">
          <Send className="w-5 h-5 mr-2" />
          {submitting ? 'Sending...' : 'Send Feedback'}
        </button>
      </form>
    </motion.div>
  )
}

export default FeedbackPage
