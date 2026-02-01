import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Check, 
  Crown, 
  Zap, 
  Shield, 
  MessageSquare, 
  Briefcase, 
  FileText, 
  BookOpen, 
  ShoppingCart,
  DollarSign,
  TrendingUp,
  CreditCard,
  AlertCircle
} from 'lucide-react'
import { useAuthStore, tierHelpers } from '../store'
import { upgradeRequestService, paymentMethodService } from '../services/api'

function UpgradePage() {
  const navigate = useNavigate()
  const { user, tierInfo, isAuthenticated } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [paymentMethods, setPaymentMethods] = useState([])
  const [selectedTier, setSelectedTier] = useState(null)
  const [selectedPayment, setSelectedPayment] = useState(null)

  const isBasic = tierHelpers.isBasic(tierInfo)
  const isProfessional = tierHelpers.isProfessional(tierInfo)
  const isPremium = tierHelpers.isPremium(tierInfo)

  useEffect(() => {
    if (isAuthenticated) {
      fetchPaymentMethods()
    }
  }, [isAuthenticated])

  const fetchPaymentMethods = async () => {
    try {
      const response = await paymentMethodService.getAll()
      setPaymentMethods(response.data.results || response.data || [])
    } catch (error) {
      console.log('Could not fetch payment methods')
    }
  }

  const handleUpgrade = async (tier) => {
    if (!isAuthenticated) {
      navigate('/register')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await upgradeRequestService.create({
        requested_tier: tier,
        payment_method: selectedPayment,
      })
      
      setSuccess(`Your ${tier} upgrade request has been submitted! We'll review it soon.`)
      setSelectedTier(null)
    } catch (error) {
      console.error('Failed to submit upgrade request:', error)
      setError(error.response?.data?.detail || 'Failed to submit upgrade request. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const tiers = [
    {
      id: 'professional',
      name: 'Professional',
      icon: Zap,
      color: 'green',
      price: 'Free',
      description: 'For professionals who want to offer consultations',
      features: [
        { name: 'Create consultation offers', included: true },
        { name: 'Message with clients', included: true },
        { name: 'Apply for jobs', included: true },
        { name: 'Post articles & research', included: true },
        { name: 'Receive reviews', included: true },
        { name: 'Basic analytics', included: true },
      ],
      current: isProfessional,
    },
    {
      id: 'premium',
      name: 'Premium Expert',
      icon: Crown,
      color: 'yellow',
      price: 'KES 5,000/year',
      description: 'For verified experts who want to maximize their earnings',
      features: [
        { name: 'All Professional features', included: true },
        { name: 'Gold verification badge', included: true },
        { name: 'Top Expert listing', included: true },
        { name: 'Sell digital products', included: true },
        { name: 'Sell merchandise', included: true },
        { name: 'Advanced analytics', included: true },
        { name: 'Priority support', included: true },
      ],
      current: isPremium,
    },
  ]

  const getColorClasses = (color) => ({
    bg: {
      green: 'bg-green-500',
      yellow: 'bg-yellow-500',
    }[color],
    light: {
      green: 'bg-green-50 dark:bg-green-900/20',
      yellow: 'bg-yellow-50 dark:bg-yellow-900/20',
    }[color],
    text: {
      green: 'text-green-600 dark:text-green-400',
      yellow: 'text-yellow-600 dark:text-yellow-400',
    }[color],
    border: {
      green: 'border-green-200 dark:border-green-800',
      yellow: 'border-yellow-200 dark:border-yellow-800',
    }[color],
    hover: {
      green: 'hover:border-green-400',
      yellow: 'hover:border-yellow-400',
    }[color],
  })

  if (!isAuthenticated) {
    return (
      <motion.div 
        initial={{ opacity: 0 }} 
        animate={{ opacity: 1 }} 
        className="max-w-4xl mx-auto text-center py-16"
      >
        <div className="w-20 h-20 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mx-auto mb-6">
          <Shield className="w-10 h-10 text-primary-600" />
        </div>
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          Upgrade Your Account
        </h1>
        <p className="text-gray-500 dark:text-gray-400 text-lg mb-8 max-w-2xl mx-auto">
          Sign up or log in to upgrade your account and unlock premium features
        </p>
        <div className="flex justify-center gap-4">
          <Link to="/register" className="btn-primary px-8 py-3">
            Create Account
          </Link>
          <Link to="/login" className="btn-outline px-8 py-3">
            Sign In
          </Link>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      className="max-w-6xl mx-auto space-y-12"
    >
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          Upgrade Your Account
        </h1>
        <p className="text-gray-500 dark:text-gray-400 text-lg max-w-2xl mx-auto">
          Choose the plan that fits your needs and unlock premium features
        </p>
      </div>

      {/* Current tier indicator */}
      {tierInfo && (
        <div className={`inline-flex items-center px-4 py-2 rounded-lg ${
          isPremium 
            ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
            : isProfessional 
              ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
        }`}>
          {isPremium ? <Crown className="w-5 h-5 mr-2" /> : isProfessional ? <Zap className="w-5 h-5 mr-2" /> : <Shield className="w-5 h-5 mr-2" />}
          <span className="font-medium">Current: {tierHelpers.getDisplayTier(tierInfo)}</span>
        </div>
      )}

      {/* Error/Success Messages */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg flex items-center">
          <AlertCircle className="w-5 h-5 mr-2" />
          {error}
          <button onClick={() => setError(null)} className="ml-auto">×</button>
        </div>
      )}
      
      {success && (
        <div className="p-4 bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 rounded-lg flex items-center">
          <Check className="w-5 h-5 mr-2" />
          {success}
          <button onClick={() => setSuccess(null)} className="ml-auto">×</button>
        </div>
      )}

      {/* Tier Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {tiers.map((tier) => {
          const colorClasses = getColorClasses(tier.color)
          const Icon = tier.icon
          const isCurrent = tier.current
          const canUpgrade = (isBasic && tier.id === 'professional') || (isProfessional && tier.id === 'premium')

          return (
            <motion.div
              key={tier.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={`card overflow-hidden ${
                selectedTier === tier.id 
                  ? `ring-2 ring-${tier.color}-500 ring-offset-2 dark:ring-offset-dark-900` 
                  : ''
              }`}
            >
              {/* Header */}
              <div className={`${colorClasses.light} p-6 border-b ${colorClasses.border}`}>
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-3 rounded-full ${colorClasses.bg} bg-opacity-10`}>
                    <Icon className={`w-8 h-8 ${colorClasses.text}`} />
                  </div>
                  {isCurrent && (
                    <span className={`badge ${colorClasses.text.replace('text-', 'bg-').replace('dark:', '')} bg-opacity-10`}>
                      Current Plan
                    </span>
                  )}
                </div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{tier.name}</h2>
                <p className="text-gray-500 dark:text-gray-400 mt-1">{tier.description}</p>
                <div className="mt-4">
                  <span className="text-4xl font-bold text-gray-900 dark:text-white">{tier.price}</span>
                </div>
              </div>

              {/* Features */}
              <div className="p-6">
                <ul className="space-y-4 mb-6">
                  {tier.features.map((feature, index) => (
                    <li key={index} className="flex items-start space-x-3">
                      <Check className={`w-5 h-5 ${colorClasses.text} flex-shrink-0 mt-0.5`} />
                      <span className="text-gray-700 dark:text-gray-300">{feature.name}</span>
                    </li>
                  ))}
                </ul>

                {/* Upgrade Button */}
                {isCurrent ? (
                  <button disabled className="btn w-full opacity-50 cursor-not-allowed">
                    Current Plan
                  </button>
                ) : canUpgrade ? (
                  <button
                    onClick={() => setSelectedTier(tier.id)}
                    className={`btn w-full ${
                      tier.color === 'yellow' 
                        ? 'bg-yellow-500 hover:bg-yellow-600 text-white' 
                        : 'bg-green-500 hover:bg-green-600 text-white'
                    }`}
                  >
                    Upgrade to {tier.name}
                  </button>
                ) : (
                  <button disabled className="btn w-full opacity-50 cursor-not-allowed">
                    {isBasic && tier.id === 'premium' ? 'Upgrade to Professional first' : 'Not available'}
                  </button>
                )}
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Payment Section */}
      {selectedTier && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-6"
        >
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            Complete Your Upgrade to {tiers.find(t => t.id === selectedTier)?.name}
          </h3>

          {/* Offline Payment Methods */}
          <div className="mb-6">
            <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-3 flex items-center">
              <CreditCard className="w-5 h-5 mr-2" />
              Payment Methods
            </h4>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              For Premium upgrade, make payment to one of these Lipa Namba numbers and upload your receipt.
            </p>

            {paymentMethods.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {paymentMethods.map((method) => (
                  <div
                    key={method.id}
                    onClick={() => setSelectedPayment(method.id)}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedPayment === method.id
                        ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                        : 'border-gray-200 dark:border-dark-700 hover:border-gray-300 dark:hover:border-dark-600'
                    }`}
                  >
                    <p className="font-medium text-gray-900 dark:text-white">{method.name}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{method.account_number}</p>
                    <p className="text-xs text-gray-400 dark:text-gray-500">{method.instructions}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                <p className="text-gray-500 dark:text-gray-400 text-sm">
                  Payment methods will be displayed here. Contact support for payment instructions.
                </p>
              </div>
            )}
          </div>

          {/* Submit Button */}
          <div className="flex gap-4">
            <button
              onClick={() => handleUpgrade(selectedTier)}
              disabled={loading || !selectedPayment}
              className="btn-primary flex-1"
            >
              {loading ? 'Submitting...' : 'Submit Upgrade Request'}
            </button>
            <button
              onClick={() => setSelectedTier(null)}
              className="btn-outline"
            >
              Cancel
            </button>
          </div>
        </motion.div>
      )}

      {/* Benefits Comparison */}
      <div className="card p-6">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
          Compare Features
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 dark:border-dark-700">
                <th className="text-left py-3 px-4 text-gray-500 dark:text-gray-400">Feature</th>
                <th className="text-center py-3 px-4 text-gray-500 dark:text-gray-400">Basic</th>
                <th className="text-center py-3 px-4 text-green-600 dark:text-green-400">Professional</th>
                <th className="text-center py-3 px-4 text-yellow-600 dark:text-yellow-400">Premium</th>
              </tr>
            </thead>
            <tbody>
              {[
                { feature: 'Browse professionals', basic: true, professional: true, premium: true },
                { feature: 'Read articles & research', basic: true, professional: true, premium: true },
                { feature: 'Message experts', basic: false, professional: true, premium: true },
                { feature: 'Initiate consultations', basic: false, professional: true, premium: true },
                { feature: 'Post articles', basic: false, professional: true, premium: true },
                { feature: 'Post research', basic: false, professional: false, premium: true },
                { feature: 'Verification badge', basic: false, professional: 'Basic', premium: 'Gold' },
                { feature: 'Sell digital items', basic: false, professional: false, premium: true },
                { feature: 'Sell merchandise', basic: false, professional: false, premium: true },
                { feature: 'Top Expert listing', basic: false, professional: false, premium: true },
                { feature: 'Advanced analytics', basic: false, professional: false, premium: true },
              ].map((row, index) => (
                <tr key={index} className="border-b border-gray-100 dark:border-dark-700">
                  <td className="py-3 px-4 text-gray-700 dark:text-gray-300">{row.feature}</td>
                  <td className="text-center py-3 px-4">
                    {typeof row.basic === 'boolean' ? (
                      row.basic ? <Check className="w-5 h-5 text-green-500 mx-auto" /> : <span className="text-gray-300">-</span>
                    ) : (
                      <span className="text-sm text-gray-500">{row.basic}</span>
                    )}
                  </td>
                  <td className="text-center py-3 px-4">
                    {typeof row.professional === 'boolean' ? (
                      row.professional ? <Check className="w-5 h-5 text-green-500 mx-auto" /> : <span className="text-gray-300">-</span>
                    ) : (
                      <span className="text-sm text-green-600 dark:text-green-400">{row.professional}</span>
                    )}
                  </td>
                  <td className="text-center py-3 px-4">
                    {typeof row.premium === 'boolean' ? (
                      row.premium ? <Check className="w-5 h-5 text-yellow-500 mx-auto" /> : <span className="text-gray-300">-</span>
                    ) : (
                      <span className="text-sm text-yellow-600 dark:text-yellow-400">{row.premium}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* FAQ */}
      <div className="card p-6">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
          Frequently Asked Questions
        </h3>
        <div className="space-y-4">
          <div className="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
            <h4 className="font-medium text-gray-900 dark:text-white mb-2">
              How do I upgrade my account?
            </h4>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Select a plan above and follow the payment instructions. Once you've made the payment, 
              submit your upgrade request with the payment details. We'll review and activate your upgrade within 24-48 hours.
            </p>
          </div>
          <div className="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
            <h4 className="font-medium text-gray-900 dark:text-white mb-2">
              Can I downgrade my account?
            </h4>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Yes, you can downgrade at any time. The new features will be removed at the end of your current billing period.
            </p>
          </div>
          <div className="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
            <h4 className="font-medium text-gray-900 dark:text-white mb-2">
              What payment methods do you accept?
            </h4>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              We accept M-Pesa (Lipa Namba), bank transfers, and credit/debit cards. 
              See the payment methods section during checkout for details.
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default UpgradePage
