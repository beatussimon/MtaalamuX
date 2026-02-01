import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Search, Star, MapPin, Users } from 'lucide-react'
import { professionalService, categoryService } from '../services/api'

function ProfessionalsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [professionals, setProfessionals] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState(searchParams.get('q') || '')
  const [selectedCategory, setSelectedCategory] = useState(searchParams.get('category') || '')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [categoriesRes] = await Promise.all([
          categoryService.getWithProfessionals(),
        ])
        setCategories(categoriesRes.data.results || categoriesRes.data)
      } catch (error) {
        console.error('Failed to fetch categories:', error)
      }
    }
    fetchData()
  }, [])

  useEffect(() => {
    const fetchProfessionals = async () => {
      setLoading(true)
      try {
        const params = {}
        if (search) params.q = search
        if (selectedCategory) params.category = selectedCategory
        
        const response = await professionalService.getAll(params)
        setProfessionals(response.data.results || response.data)
      } catch (error) {
        console.error('Failed to fetch professionals:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchProfessionals()
  }, [search, selectedCategory])

  const handleSearch = (e) => {
    e.preventDefault()
    const params = new URLSearchParams()
    if (search) params.set('q', search)
    if (selectedCategory) params.set('category', selectedCategory)
    setSearchParams(params)
  }

  return (
    <div className="space-y-8">
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
            onChange={(e) => setSelectedCategory(e.target.value)}
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

      {/* Category filters */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setSelectedCategory('')}
          className={`badge text-sm px-4 py-2 ${
            !selectedCategory
              ? 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200'
              : 'bg-gray-100 text-gray-700 dark:bg-dark-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-dark-600'
          }`}
        >
          All
        </button>
        {categories.map((category) => (
          <button
            key={category.id}
            onClick={() => setSelectedCategory(category.name)}
            className={`badge text-sm px-4 py-2 ${
              selectedCategory === category.name
                ? 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200'
                : 'bg-gray-100 text-gray-700 dark:bg-dark-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-dark-600'
            }`}
          >
            {category.name}
          </button>
        ))}
      </div>

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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {professionals.map((professional) => (
            <Link
              key={professional.id}
              to={`/professionals/${professional.id}`}
              className="card p-6 hover:shadow-lg transition-all duration-300 group"
            >
              <div className="flex items-start space-x-4">
                <div className="w-16 h-16 rounded-full overflow-hidden ring-2 ring-primary-100 dark:ring-primary-900 flex-shrink-0">
                  {professional.photo ? (
                    <img
                      src={professional.photo}
                      alt={professional.user?.username}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                      <span className="text-xl font-bold text-primary-600 dark:text-primary-400">
                        {professional.user?.username?.charAt(0).toUpperCase()}
                      </span>
                    </div>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors truncate">
                    {professional.user?.username}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {professional.field?.name}
                  </p>
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
                      {professional.average_rating?.toFixed(1) || '0.0'}
                    </span>
                  </div>
                  <div className="flex items-center space-x-1 text-sm text-gray-500 dark:text-gray-400">
                    <Users className="w-4 h-4" />
                    <span>{professional.follower_count || 0} followers</span>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">
            No professionals found matching your criteria
          </p>
        </div>
      )}
    </div>
  )
}

export default ProfessionalsPage
