import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Briefcase, MapPin, Clock, DollarSign } from 'lucide-react'
import { jobService, externalJobService } from '../services/api'

function JobsPage() {
  const [jobs, setJobs] = useState([])
  const [externalJobs, setExternalJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('internal')

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const [internalRes, externalRes] = await Promise.all([
          jobService.getAll({ status: 'open' }),
          externalJobService.getAll({ is_active: true }),
        ])
        setJobs(internalRes.data.results || internalRes.data)
        setExternalJobs(externalRes.data.results || externalRes.data)
      } catch (error) {
        console.error('Failed to fetch jobs:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchJobs()
  }, [])

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Job Opportunities</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Find your next opportunity</p>
      </div>

      <div className="flex space-x-4 border-b border-gray-200 dark:border-dark-700">
        <button
          onClick={() => setActiveTab('internal')}
          className={`pb-4 px-4 font-medium transition-colors ${
            activeTab === 'internal'
              ? 'text-primary-600 border-b-2 border-primary-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Internal Jobs
        </button>
        <button
          onClick={() => setActiveTab('external')}
          className={`pb-4 px-4 font-medium transition-colors ${
            activeTab === 'external'
              ? 'text-primary-600 border-b-2 border-primary-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          External Jobs
        </button>
      </div>

      {loading ? (
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="card p-6 animate-pulse">
              <div className="h-6 bg-gray-200 dark:bg-dark-700 rounded w-1/3 mb-4" />
              <div className="h-4 bg-gray-200 dark:bg-dark-700 rounded w-1/4 mb-2" />
              <div className="h-4 bg-gray-200 dark:bg-dark-700 rounded w-2/3" />
            </div>
          ))}
        </div>
      ) : activeTab === 'internal' ? (
        <div className="space-y-4">
          {jobs.length > 0 ? (
            jobs.map((job) => (
              <motion.div key={job.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card p-6 hover:shadow-lg transition-shadow">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white">{job.title}</h3>
                    <p className="text-gray-500 dark:text-gray-400 mt-1">{job.description?.substring(0, 150)}...</p>
                    <div className="flex flex-wrap items-center gap-4 mt-3 text-sm text-gray-500">
                      <span className="flex items-center space-x-1">
                        <MapPin className="w-4 h-4" />
                        <span>Remote</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <DollarSign className="w-4 h-4" />
                        <span>{job.budget ? `$${job.budget}` : 'Negotiable'}</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <Clock className="w-4 h-4" />
                        <span>{new Date(job.created_at).toLocaleDateString()}</span>
                      </span>
                    </div>
                  </div>
                  <button className="btn-primary mt-4 md:mt-0">Apply Now</button>
                </div>
              </motion.div>
            ))
          ) : (
            <div className="text-center py-12">
              <Briefcase className="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
              <p className="text-gray-500 dark:text-gray-400">No open positions at the moment</p>
            </div>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {externalJobs.length > 0 ? (
            externalJobs.map((job) => (
              <motion.div key={job.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="badge-primary mb-2">{job.job_type}</span>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{job.title}</h3>
                    <p className="text-sm text-gray-500 mt-1">{job.category?.name}</p>
                  </div>
                </div>
                <p className="text-gray-600 dark:text-gray-300 mt-3 text-sm">{job.description?.substring(0, 200)}...</p>
                <div className="flex flex-wrap items-center gap-3 mt-4 text-sm text-gray-500">
                  <span className="flex items-center space-x-1">
                    <MapPin className="w-4 h-4" />
                    <span>{job.location || 'Remote'}</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <DollarSign className="w-4 h-4" />
                    <span>{job.budget ? `$${job.budget}` : 'Not specified'}</span>
                  </span>
                </div>
                {job.apply_url && (
                  <a href={job.apply_url} target="_blank" rel="noopener noreferrer" className="btn-outline w-full mt-4 text-center">
                    Apply Now
                  </a>
                )}
              </motion.div>
            ))
          ) : (
            <div className="col-span-2 text-center py-12">
              <Briefcase className="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
              <p className="text-gray-500 dark:text-gray-400">No external jobs available</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default JobsPage
