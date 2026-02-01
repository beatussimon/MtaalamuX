import { useState, useEffect, useCallback } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Search, Star, MapPin, Users, Filter, ChevronLeft, ChevronRight, Shield, AlertCircle } from 'lucide-react'
import { professionalService, categoryService } from '../services/api'

function ProfessionalsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [professionals, setProfessionals] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState(searchParams.get('q') || '')
  const [selectedCategory, setSelectedCategory] = useState(searchParams.get('category') || '')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [showFilters, setShowFilters] = useState(false)
  const [verificationFilter, setVerificationFilter] = useState('')

  const fetchCategories = useCallback(async () => {
    try {
      const categoriesRes = await categoryService.getWithProfessionals()
      setCategories(categoriesRes.data.results || categoriesRes.data)
    } catch (error) {
      console.error('Failed to fetch categories:', error)
    }
  }, [])

  const fetchProfessionals = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = {
        page,
        limit: 12,
      }
      if (search) params.q = search
      if (selectedCategory) params.category = selectedCategory
      if (verificationFilter) params.verification = verificationFilter
      
      const response = await professionalService.getAll(params)
      setProfessionals(response.data.results || response.data || [])
      const totalCount = response.data.count || response.data.length || 0
      setTotalPages(Math.ceil(totalCount / 12))
    } catch (error) {
      console.error('Failed to fetch professionals:', error)
      setError('Failed to load professionals. Please try again.')
      setProfessionals([])
    } finally {
      setLoading(false)
    }
  }, [page, search, selectedCategory, verificationFilter])

  useEffect(() => {
    fetchCategories()
  }, [fetchCategories])

  useEffect(() => {
    fetchProfessionals()
  }, [fetchProfessionals])

  const handleSearch = (e) => {
    e.preventDefault()
    const params = new URLSearchParams()
    if (search) params.set('q', search)
    if (selectedCategory) params.set('category', selectedCategory)
    setSearchParams(params)
    setPage(1)
  }

  const getVerificationBadge = (professional) => {
    if (!professional.is_verified) return null
    
    return (
      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ml-1 ${
        professional.verification_level === 'gold'
          ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
          : 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
      }`} title={`${professional.verification_level || 'verified'} verified expert`}>
        <Shield className="w-3 h-3 mr-1" />
        {professional.verification_level === 'gold' ? 'Gold' : 'Verified'}
      </span>
    )
  }

  const getVerificationCheckmark = (professional) => {
    if (!professional.is_verified) return null
    
    return (
      <div className={`absolute bottom-0 right-0 w-6 h-6 rounded-full flex items-center justify-center ${
        professional.verification_level === 'gold'
          ? 'bg-yellow-400'
          : 'bg-green-500'
      }`}>
        <span className="text-white text-xs font-bold">✓</span>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Professionals
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Find and connect with verified professionals
          </p>
        </div>

        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="relative flex-1 md:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search professionals..."
              className="input pl-10"
            />
          </div>
          <select
            value={selectedCategory}
            onChange={(e) => {
              setSelectedCategory(e.target.value)
              setPage(1)
            }}
            className="input w-auto"
          >
            <option value="">All Categories</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.name}>
                {cat.name}
              </option>
            ))}
          </select>
          <button type="submit" className="btn-primary">
            Search
          </button>
        </form>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg flex items-center">
          <AlertCircle className="w-5 h-5 mr-2" />
          {error}
          <button onClick={fetchProfessionals} className="ml-auto underline text-sm">
            Retry
          </button>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-4 items-center">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`btn-outline flex items-center gap-2 ${showFilters ? 'bg-primary-50 dark:bg-primary-900/20' : ''}`}
        >
          <Filter className="w-4 h-4" />
          More Filters
        </button>

        <select
          value={verificationFilter}
          onChange={(e) => {
            setVerificationFilter(e.target.value)
            setPage(1)
          }}
          className="input w-auto"
        >
          <option value="">All Verification Levels</option>
          <option value="gold">Gold Verified</option>
          <option value="silver">Silver Verified</option>
          <option value="basic">Basic Verified</option>
        </select>

        {/* Category quick filters */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => {
              setSelectedCategory('')
              setPage(1)
            }}
            className={`badge text-sm px-3 py-1.5 cursor-pointer ${
              !selectedCategory
                ? 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200'
                : 'bg-gray-100 text-gray-700 dark:bg-dark-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-dark-600'
            }`}
          >
            All
          </button>
          {categories.slice(0, 6).map((category) => (
            <button
              key={category.id}
              onClick={() => {
                setSelectedCategory(category.name)
                setPage(1)
              }}
              className={`badge text-sm px-3 py-1.5 cursor-pointer ${
                selectedCategory === category.name
                  ? 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200'
                  : 'bg-gray-100 text-gray-700 dark:bg-dark-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-dark-600'
              }`}
            >
              {category.name}
            </button>
          ))}
        </div>
      </div>

      {/* Results count */}
      {!loading && professionals.length > 0 && (
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Showing {professionals.length} professional{professionals.length !== 1 ? 's' : ''}
        </p>
      )}

      {/* Results */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(9)].map((_, i) => (
            <div key={i} className="card p-6 animate-pulse">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-gray-200 dark:bg-dark-700 rounded-full" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 dark:bg-dark-700 rounded w-3/4" />
                  <div className="h-3 bg-gray-200 dark:bg-dark-700 rounded w-1/2" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : professionals.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {professionals.map((professional) => (
              <Link
                key={professional.id}
                to={`/professionals/${professional.id}`}
                className="card p-6 hover:shadow-lg transition-all duration-300 group"
              >
                <div className="flex items-start space-x-4">
                  <div className="relative w-16 h-16 rounded-full overflow-hidden ring-2 ring-primary-100 dark:ring-primary-900 flex-shrink-0">
                    {professional.photo ? (
                      <img
                        src={professional.photo}
                        alt={professional.user?.username}
                        loading="lazy"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                        <span className="text-xl font-bold text-primary-600 dark:text-primary-400">
                          {professional.user?.username?.charAt(0).toUpperCase()}
                        </span>
                      </div>
                    )}
                    {getVerificationCheckmark(professional)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors truncate flex items-center">
                      {professional.user?.username}
                      {getVerificationBadge(professional)}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {professional.field?.name || professional.specialization}
                    </p>
                    {professional.subfield && (
                      <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
                        {professional.subfield}
                      </p>
                    )}
                    {professional.location && (
                      <div className="flex items-center space-x-1 mt-1 text-sm text-gray-500 dark:text-gray-400">
                        <MapPin className="w-3 h-3" />
                        <span>{professional.location}</span>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="mt-4 pt-4 border-t border-gray-100 dark:border-dark-700">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-1">
                      <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        {professional.avg_rating?.toFixed(1) || '0.0'}
                      </span>
                      {professional.review_count > 0 && (
                        <span className="text-xs text-gray-500">({professional.review_count})</span>
                      )}
                    </div>
                    <div className="flex items-center space-x-1 text-sm text-gray-500 dark:text-gray-400">
                      <Users className="w-4 h-4" />
                      <span>{professional.followers_count || 0}</span>
                    </div>
                  </div>
                </div>

                {/* Quick stats */}
                <div className="mt-3 flex gap-2 text-xs text-gray-500">
                  {professional.article_count > 0 && (
                    <span>{professional.article_count} articles</span>
                  )}
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
            <Users className="w-8 h-8 text-gray-400" />
          </div>
          <p className="text-gray-500 dark:text-gray-400 mb-2">
            No professionals found matching your criteria
          </p>
          <p className="text-sm text-gray-400 dark:text-gray-500">
            Try adjusting your search or filters
          </p>
        </div>
      )}
    </div>
  )
}

export default ProfessionalsPage
