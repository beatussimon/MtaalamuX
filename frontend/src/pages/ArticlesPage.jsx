import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Search, Star, Eye, Calendar, User } from 'lucide-react'
import { articleService, categoryService } from '../services/api'

function ArticlesPage() {
  const [articles, setArticles] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [articlesRes, categoriesRes] = await Promise.all([
          articleService.getAll({ limit: 20 }),
          categoryService.getAll(),
        ])
        setArticles(articlesRes.data.results || articlesRes.data)
        setCategories(categoriesRes.data.results || categoriesRes.data)
      } catch (error) {
        console.error('Failed to fetch data:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const filteredArticles = articles.filter(article => {
    const matchesSearch = !search || 
      article.title.toLowerCase().includes(search.toLowerCase()) ||
      article.content?.toLowerCase().includes(search.toLowerCase())
    const matchesCategory = !selectedCategory || article.category?.name === selectedCategory
    return matchesSearch && matchesCategory
  })

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Articles & Insights
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Discover articles from our professional community
        </p>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search articles..."
            className="input pl-10"
          />
        </div>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="input w-auto md:w-48"
        >
          <option value="">All Categories</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.name}>{cat.name}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="card overflow-hidden animate-pulse">
              <div className="h-48 bg-gray-200 dark:bg-dark-700" />
              <div className="p-4 space-y-3">
                <div className="h-4 bg-gray-200 dark:bg-dark-700 rounded w-3/4" />
                <div className="h-3 bg-gray-200 dark:bg-dark-700 rounded w-full" />
              </div>
            </div>
          ))}
        </div>
      ) : filteredArticles.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredArticles.map((article) => (
            <Link key={article.id} to={`/articles/${article.id}`} className="card overflow-hidden group">
              <div className="h-48 overflow-hidden">
                {article.image ? (
                  <img src={article.image} alt={article.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center">
                    <span className="text-white text-4xl font-bold">{article.title?.charAt(0)}</span>
                  </div>
                )}
              </div>
              <div className="p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="badge-primary">{article.category?.name}</span>
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-primary-600 transition-colors line-clamp-2">
                  {article.title}
                </h3>
                <div className="flex items-center space-x-4 mt-4 text-sm text-gray-500">
                  <span className="flex items-center space-x-1">
                    <User className="w-4 h-4" />
                    <span>{article.author?.user?.username}</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <Calendar className="w-4 h-4" />
                    <span>{new Date(article.publish_date).toLocaleDateString()}</span>
                  </span>
                </div>
                <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                  <span className="flex items-center space-x-1">
                    <Star className="w-4 h-4" />
                    <span>{article.like_count || 0}</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <Eye className="w-4 h-4" />
                    <span>{article.views || 0}</span>
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">No articles found</p>
        </div>
      )}
    </div>
  )
}

export default ArticlesPage
