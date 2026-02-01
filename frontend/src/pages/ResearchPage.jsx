import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Search, Star, Eye, Calendar, User, Filter, ChevronLeft, ChevronRight, Shield, BookOpen, AlertCircle } from 'lucide-react'
import { researchService, categoryService } from '../services/api'
import { useAuthStore } from '../store'

function ResearchPage() {
  const { isAuthenticated, tierInfo } = useAuthStore()
  const [research, setResearch] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [showFilters, setShowFilters] = useState(false)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = {
        page,
        limit: 12,
      }
      if (search) params.q = search
      if (selectedCategory) params.category = selectedCategory

      const [researchRes, categoriesRes] = await Promise.all([
        researchService.getAll(params),
        categoryService.getAll(),
      ])
      
      setResearch(researchRes.data.results || researchRes.data || [])
      const totalCount = researchRes.data.count || researchRes.data.length || 0
      setTotalPages(Math.ceil(totalCount / 12))
      setCategories(categoriesRes.data.results || categoriesRes.data || [])
    } catch (error) {
      console.error('Failed to fetch data:', error)
      setError('Failed to load research. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [page, search, selectedCategory])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const handleSearch = (e) => {
    e.preventDefault()
    setPage(1)
    fetchData()
  }

  const handleCategoryChange = (category) => {
    setSelectedCategory(category)
    setPage(1)
  }

  const getVerificationBadge = (author) => {
    if (!author?.is_verified) return null
    
    return (
      <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium ${
        author.verification_level === 'gold'
          ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
          : 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
      }`} title={`${author.verification_level || 'verified'} verified expert`}>
        <Shield className="w-3 h-3 mr-1" />
        {author.verification_level === 'gold' ? 'Gold' : 'Verified'}
      </span>
    )
  }

  const formatAbstract = (abstract) => {
    if (!abstract) return ''
    return abstract.replace(/<[^>]*>/g, '').substring(0, 150)
  }

  const filteredResearch = research.filter(item => {
    const matchesSearch = !search || 
      item.title?.toLowerCase().includes(search.toLowerCase()) ||
      item.abstract?.toLowerCase().includes(search.toLowerCase())
    const matchesCategory = !selectedCategory || item.category?.name === selectedCategory
    return matchesSearch && matchesCategory
  })

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Research & Publications
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Explore research papers and publications from verified experts
        </p>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg flex items-center">
          <AlertCircle className="w-5 h-5 mr-2" />
          {error}
          <button onClick={fetchData} className="ml-auto underline text-sm">
            Retry
          </button>
        </div>
      )}

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <form onSubmit={handleSearch} className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search research..."
            className="input pl-10"
          />
        </form>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`btn-outline flex items-center gap-2 ${showFilters ? 'bg-primary-50 dark:bg-primary-900/20' : ''}`}
        >
          <Filter className="w-4 h-4" />
          Filters
        </button>
      </div>

      {/* Category filters */}
      {showFilters && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="flex flex-wrap gap-2"
        >
          <button
            onClick={() => handleCategoryChange('')}
            className={`badge text-sm px-4 py-2 cursor-pointer ${
              !selectedCategory
                ? 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200'
                : 'bg-gray-100 text-gray-700 dark:bg-dark-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-dark-600'
            }`}
          >
            All Categories
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => handleCategoryChange(cat.name)}
              className={`badge text-sm px-4 py-2 cursor-pointer ${
                selectedCategory === cat.name
                  ? 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200'
                  : 'bg-gray-100 text-gray-700 dark:bg-dark-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-dark-600'
              }`}
            >
              {cat.name}
            </button>
          ))}
        </motion.div>
      )}

      {/* Active filters */}
      {(search || selectedCategory) && (
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">Active filters:</span>
          {search && (
            <span className="badge badge-primary text-sm">
              Search: {search}
              <button onClick={() => setSearch('')} className="ml-1 hover:text-red-500">×</button>
            </span>
          )}
          {selectedCategory && (
            <span className="badge badge-primary text-sm">
              Category: {selectedCategory}
              <button onClick={() => handleCategoryChange('')} className="ml-1 hover:text-red-500">×</button>
            </span>
          )}
        </div>
      )}

      {/* Research Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="card overflow-hidden animate-pulse">
              <div className="h-40 bg-gray-200 dark:bg-dark-700" />
              <div className="p-4 space-y-3">
                <div className="h-4 bg-gray-200 dark:bg-dark-700 rounded w-3/4" />
                <div className="h-3 bg-gray-200 dark:bg-dark-700 rounded w-full" />
                <div className="h-3 bg-gray-200 dark:bg-dark-700 rounded w-2/3" />
              </div>
            </div>
          ))}
        </div>
      ) : filteredResearch.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredResearch.map((item) => (
              <Link key={item.id} to={`/research/${item.id}`} className="card overflow-hidden group">
                <div className="h-40 overflow-hidden bg-gradient-to-br from-cyan-400 to-cyan-600 relative">
                  {item.image ? (
                    <img 
                      src={item.image} 
                      alt={item.title}
                      loading="lazy"
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" 
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <BookOpen className="w-12 h-12 text-white/50" />
                    </div>
                  )}
                  <div className="absolute top-2 right-2">
                    {item.status === 'published' ? (
                      <span className="badge bg-white/90 text-cyan-700 text-xs">Published</span>
                    ) : (
                      <span className="badge bg-yellow-100 text-yellow-700 text-xs">Draft</span>
                    )}
                  </div>
                </div>
                <div className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="badge-cyan text-xs">{item.category?.name}</span>
                    {getVerificationBadge(item.author)}
                  </div>
                  <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors line-clamp-2">
                    {item.title}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 line-clamp-3">
                    {formatAbstract(item.abstract)}...
                  </p>
                  <div className="flex items-center space-x-4 mt-4 text-sm text-gray-500">
                    <span className="flex items-center space-x-1">
                      <User className="w-4 h-4" />
                      <span>{item.author?.user?.username}</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <Calendar className="w-4 h-4" />
                      <span>{new Date(item.publish_date).toLocaleDateString()}</span>
                    </span>
                  </div>
                  <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                    <span className="flex items-center space-x-1">
                      <Star className="w-4 h-4" />
                      <span>{item.like_count || 0}</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <Eye className="w-4 h-4" />
                      <span>{item.views || 0}</span>
                    </span>
                    <span className="text-xs text-gray-400">
                      {item.download_count || 0} downloads
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="btn-outline p-2 disabled:opacity-50"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <span className="text-gray-500 dark:text-gray-400">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="btn-outline p-2 disabled:opacity-50"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 dark:bg-dark-800 rounded-full flex items-center justify-center mx-auto mb-4">
            <BookOpen className="w-8 h-8 text-gray-400" />
          </div>
          <p className="text-gray-500 dark:text-gray-400 mb-2">No research found</p>
          <p className="text-sm text-gray-400 dark:text-gray-500">
            {search || selectedCategory ? 'Try adjusting your search or filters' : 'Check back later for new research'}
          </p>
          {isAuthenticated && (
            <Link to="/research/new" className="btn-primary mt-4 inline-block">
              Publish Research
            </Link>
          )}
        </div>
      )}
    </div>
  )
}

export default ResearchPage
