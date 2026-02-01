import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, Users, BookOpen, Briefcase, Star, TrendingUp } from 'lucide-react'
import { categoryService, articleService, professionalService } from '../services/api'

function HomePage() {
  const [categories, setCategories] = useState([])
  const [articles, setArticles] = useState([])
  const [topProfessionals, setTopProfessionals] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [categoriesRes, articlesRes, professionalsRes] = await Promise.all([
          categoryService.getWithProfessionals(),
          articleService.getAll({ limit: 6 }),
          professionalService.getAll({ limit: 4 }),
        ])
        setCategories(categoriesRes.data.results || categoriesRes.data)
        setArticles(articlesRes.data.results || articlesRes.data)
        setTopProfessionals(professionalsRes.data.results || professionalsRes.data)
      } catch (error) {
        console.error('Failed to fetch data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-16"
    >
      {/* Hero Section */}
      <section className="relative -mt-8 -mx-4 px-4 py-20 bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 rounded-3xl overflow-hidden">
        <div className="absolute inset-0 bg-black/10" />
        <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-primary-400/20 rounded-full blur-3xl" />
        
        <div className="relative container mx-auto text-center">
          <motion.h1
            variants={itemVariants}
            className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6"
          >
            Connect with
            <span className="block text-primary-200">Professionals</span>
          </motion.h1>
          <motion.p
            variants={itemVariants}
            className="text-lg md:text-xl text-primary-100 max-w-2xl mx-auto mb-8"
          >
            Discover talented professionals, explore insightful articles, and find your next opportunity on MtaalamuX.
          </motion.p>
          <motion.div
            variants={itemVariants}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link to="/professionals" className="btn bg-white text-primary-600 hover:bg-primary-50 px-8 py-3">
              Explore Professionals
            </Link>
            <Link to="/register" className="btn border-2 border-white text-white hover:bg-white/10 px-8 py-3">
              Join Now
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {[
          { icon: Users, label: 'Professionals', value: '10K+' },
          { icon: BookOpen, label: 'Articles', value: '5K+' },
          { icon: Briefcase, label: 'Jobs', value: '2K+' },
          { icon: Star, label: 'Reviews', value: '50K+' },
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            variants={itemVariants}
            className="card p-6 text-center"
          >
            <stat.icon className="w-8 h-8 mx-auto mb-3 text-primary-600 dark:text-primary-400" />
            <p className="text-3xl font-bold text-gray-900 dark:text-white">{stat.value}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">{stat.label}</p>
          </motion.div>
        ))}
      </section>

      {/* Categories Section */}
      <section>
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">
            Browse by Category
          </h2>
          <Link to="/professionals" className="link flex items-center space-x-1">
            <span>View all</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="card p-6 h-32 animate-pulse">
                <div className="h-12 w-12 bg-gray-200 dark:bg-dark-700 rounded-lg mb-3" />
                <div className="h-4 bg-gray-200 dark:bg-dark-700 rounded w-3/4" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {categories.map((category) => (
              <Link
                key={category.id}
                to={`/professionals?category=${category.name}`}
                className="card p-6 hover:shadow-lg transition-all duration-300 group"
              >
                <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                  <span className="text-xl font-bold text-primary-600 dark:text-primary-400">
                    {category.initials || category.name?.charAt(0)}
                  </span>
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                  {category.name}
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {category.professional_count || 0} professionals
                </p>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* Top Professionals Section */}
      <section>
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">
            Top Professionals
          </h2>
          <Link to="/professionals" className="link flex items-center space-x-1">
            <span>View all</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="card p-6 animate-pulse">
                <div className="h-24 w-24 bg-gray-200 dark:bg-dark-700 rounded-full mx-auto mb-4" />
                <div className="h-4 bg-gray-200 dark:bg-dark-700 rounded w-3/4 mx-auto mb-2" />
                <div className="h-3 bg-gray-200 dark:bg-dark-700 rounded w-1/2 mx-auto" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {topProfessionals.map((professional) => (
              <Link
                key={professional.id}
                to={`/professionals/${professional.id}`}
                className="card p-6 hover:shadow-lg transition-all duration-300 group"
              >
                <div className="text-center">
                  <div className="w-24 h-24 mx-auto mb-4 rounded-full overflow-hidden ring-2 ring-primary-100 dark:ring-primary-900">
                    {professional.photo ? (
                      <img
                        src={professional.photo}
                        alt={professional.user?.username}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                        <span className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                          {professional.user?.username?.charAt(0).toUpperCase()}
                        </span>
                      </div>
                    )}
                  </div>
                  <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                    {professional.user?.username}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                    {professional.field?.name}
                  </p>
                  <div className="flex items-center justify-center space-x-1">
                    <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {professional.average_rating?.toFixed(1) || '0.0'}
                    </span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      ({professional.follower_count || 0} followers)
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* Featured Articles Section */}
      <section>
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">
            Featured Articles
          </h2>
          <Link to="/articles" className="link flex items-center space-x-1">
            <span>View all</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="card overflow-hidden animate-pulse">
                <div className="h-48 bg-gray-200 dark:bg-dark-700" />
                <div className="p-4 space-y-3">
                  <div className="h-4 bg-gray-200 dark:bg-dark-700 rounded w-3/4" />
                  <div className="h-3 bg-gray-200 dark:bg-dark-700 rounded w-full" />
                  <div className="h-3 bg-gray-200 dark:bg-dark-700 rounded w-2/3" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {articles.map((article) => (
              <Link
                key={article.id}
                to={`/articles/${article.id}`}
                className="card overflow-hidden group"
              >
                <div className="h-48 overflow-hidden">
                  {article.image ? (
                    <img
                      src={article.image}
                      alt={article.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center">
                      <BookOpen className="w-12 h-12 text-white/50" />
                    </div>
                  )}
                </div>
                <div className="p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="badge-primary">{article.category?.name}</span>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {new Date(article.publish_date).toLocaleDateString()}
                    </span>
                  </div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                    {article.title}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2">
                    {article.content?.replace(/<[^>]*>/g, '').substring(0, 100)}...
                  </p>
                  <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100 dark:border-dark-700">
                    <div className="flex items-center space-x-2">
                      <div className="w-6 h-6 rounded-full overflow-hidden">
                        {article.author?.photo ? (
                          <img
                            src={article.author.photo}
                            alt={article.author?.user?.username}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full bg-primary-100 dark:bg-primary-900" />
                        )}
                      </div>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {article.author?.user?.username}
                      </span>
                    </div>
                    <div className="flex items-center space-x-3 text-sm text-gray-500 dark:text-gray-400">
                      <span className="flex items-center space-x-1">
                        <Star className="w-4 h-4" />
                        <span>{article.like_count || 0}</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <TrendingUp className="w-4 h-4" />
                        <span>{article.views || 0}</span>
                      </span>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* CTA Section */}
      <section className="card p-8 md:p-12 bg-gradient-to-r from-primary-600 to-primary-800 rounded-2xl">
        <div className="text-center">
          <h2 className="text-2xl md:text-3xl font-bold text-white mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-primary-100 mb-8 max-w-xl mx-auto">
            Join thousands of professionals and clients on MtaalamuX. Create your profile, connect with others, and grow your career.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/register" className="btn bg-white text-primary-600 hover:bg-primary-50 px-8 py-3">
              Create Free Account
            </Link>
            <Link to="/faq" className="btn border-2 border-white text-white hover:bg-white/10 px-8 py-3">
              Learn More
            </Link>
          </div>
        </div>
      </section>
    </motion.div>
  )
}

export default HomePage
