import axios from 'axios'
import { useAuthStore } from '../store'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
})

// Retry logic for 429 errors with exponential backoff
const retryRequest = async (error, maxRetries = 5) => {
  const originalRequest = error.config
  
  if (!originalRequest || !originalRequest._retry) {
    originalRequest._retry = 0
  }
  
  if (originalRequest._retry >= maxRetries) {
    return Promise.reject(error)
  }
  
  // Only retry on 429 (rate limit) errors
  if (error.response?.status === 429) {
    originalRequest._retry++
    
    // Check for Retry-After header first
    let delay
    const retryAfter = error.response.headers['retry-after']
    if (retryAfter) {
      // If Retry-After is in seconds, parse it
      const seconds = parseInt(retryAfter, 10)
      // Cap the delay to 10 seconds max to avoid hanging the UI
      delay = Math.min(seconds * 1000, 10000)
    } else {
      // Exponential backoff: 100ms, 200ms, 400ms, 800ms, 1600ms...
      delay = Math.min(Math.pow(2, originalRequest._retry) * 100, 10000)
    }
    
    console.warn(`Rate limited. Retrying in ${delay}ms (attempt ${originalRequest._retry}/${maxRetries})`)
    await new Promise(resolve => setTimeout(resolve, delay))
    
    return api(originalRequest)
  }
  
  return Promise.reject(error)
}

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Set higher default limit for list endpoints
    if (config.method === 'get' && !config.params?.limit) {
      if (config.url?.includes('/articles') || 
          config.url?.includes('/research') || 
          config.url?.includes('/professionals') ||
          config.url?.includes('/jobs')) {
        config.params = { ...config.params, limit: 100 }
      }
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor with retry logic
api.interceptors.response.use(
  response => response,
  async (error) => {
    // Try retry for 429 errors
    if (error.response?.status === 429) {
      try {
        return await retryRequest(error)
      } catch (retryError) {
        return Promise.reject(retryError)
      }
    }
    
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        // Get refresh token from persisted store
        const storedData = localStorage.getItem('auth-storage')
        const { state } = JSON.parse(storedData || '{}')
        const refreshToken = state?.refreshToken

        if (refreshToken) {
          const response = await axios.post('/api/v1/auth/refresh/', {
            refresh: refreshToken,
          })

          const { access } = response.data
          useAuthStore.getState().setToken(access)
          originalRequest.headers.Authorization = `Bearer ${access}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed - clear auth state and redirect to login
        useAuthStore.getState().logout()
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api

// API service functions

// Auth Service
export const authService = {
  login: (credentials) => api.post('/api/v1/auth/login/', credentials),
  register: (userData) => api.post('/api/v1/auth/register/', userData),
  refreshToken: (refresh) => api.post('/api/v1/auth/refresh/', { refresh }),
}

// User Service
export const userService = {
  getCurrentUser: () => api.get('/api/v1/users/me/'),
  updateProfile: (data) => api.put('/api/v1/users/update_profile/', data),
  getTierInfo: () => api.get('/api/v1/users/tier_info/'),
}

// Category Service
export const categoryService = {
  getAll: () => api.get('/api/v1/categories/'),
  getWithProfessionals: () => api.get('/api/v1/categories/with_professionals/'),
}

// Professional Service
export const professionalService = {
  getAll: (params) => api.get('/api/v1/professionals/', { params }),
  getById: (id) => api.get(`/api/v1/professionals/${id}/`),
  follow: (id) => api.post(`/api/v1/professionals/${id}/follow/`),
  getArticles: (id) => api.get(`/api/v1/professionals/${id}/articles/`),
  getResearch: (id) => api.get(`/api/v1/professionals/${id}/research/`),
  getReviews: (id) => api.get(`/api/v1/professionals/${id}/reviews/`),
  getPortfolio: (id) => api.get(`/api/v1/professionals/${id}/portfolio/`),
}

// Article Service
export const articleService = {
  getAll: (params) => api.get('/api/v1/articles/', { params }),
  getById: (id) => api.get(`/api/v1/articles/${id}/`),
  create: (data) => api.post('/api/v1/articles/', data),
  like: (id) => api.post(`/api/v1/articles/${id}/like/`),
  share: (id) => api.post(`/api/v1/articles/${id}/share/`),
  getComments: (id) => api.get(`/api/v1/articles/${id}/comments/`),
  getTrending: () => api.get('/api/v1/articles/trending/'),
  getTop: () => api.get('/api/v1/articles/top/'),
}

// Research Service
export const researchService = {
  getAll: (params) => api.get('/api/v1/research/', { params }),
  getById: (id) => api.get(`/api/v1/research/${id}/`),
  create: (data) => api.post('/api/v1/research/', data),
  like: (id) => api.post(`/api/v1/research/${id}/like/`),
  share: (id) => api.post(`/api/v1/research/${id}/share/`),
  getTop: () => api.get('/api/v1/research/top/'),
}

// Consultation Service
export const consultationService = {
  getAll: (params) => api.get('/api/v1/consultations/', { params }),
  getById: (id) => api.get(`/api/v1/consultations/${id}/`),
  create: (data) => api.post('/api/v1/consultations/', data),
  getMyConsultations: () => api.get('/api/v1/consultations/my_consultations/'),
  getAsClient: () => api.get('/api/v1/consultations/as_client/'),
  getAsExpert: () => api.get('/api/v1/consultations/as_expert/'),
}

// Consultation Task Service
export const consultationTaskService = {
  getAll: (params) => api.get('/api/v1/consultation-tasks/', { params }),
  getById: (id) => api.get(`/api/v1/consultation-tasks/${id}/`),
  create: (data) => api.post('/api/v1/consultation-tasks/', data),
  getMyTasks: () => api.get('/api/v1/consultation-tasks/my_tasks/'),
  apply: (id, data) => api.post(`/api/v1/consultation-tasks/${id}/apply/`, data),
}

// Consultation Application Service
export const consultationApplicationService = {
  getAll: (params) => api.get('/api/v1/consultation-applications/', { params }),
  getMyApplications: () => api.get('/api/v1/consultation-applications/my_applications/'),
  getReceived: () => api.get('/api/v1/consultation-applications/received/'),
}

// Conversation Service
export const conversationService = {
  getAll: () => api.get('/api/v1/conversations/'),
  getById: (id) => api.get(`/api/v1/conversations/${id}/`),
  create: (data) => api.post('/api/v1/conversations/', data),
  getMessages: (id) => api.get(`/api/v1/conversations/${id}/messages/`),
}

// Message Service
export const messageService = {
  getInbox: () => api.get('/api/v1/messages/inbox/'),
  getSent: () => api.get('/api/v1/messages/sent/'),
  getConversation: (userId) => api.get('/api/v1/messages/conversation/', { params: { user_id: userId } }),
  send: (data) => api.post('/api/v1/messages/', data),
  markAsRead: (id) => api.post(`/api/v1/messages/${id}/mark_read/`),
  markAllAsRead: () => api.post('/api/v1/messages/mark_all_read/'),
}

// Payment Method Service
export const paymentMethodService = {
  getAll: () => api.get('/api/v1/payment-methods/'),
  getById: (id) => api.get(`/api/v1/payment-methods/${id}/`),
}

// Payment Record Service
export const paymentRecordService = {
  getAll: (params) => api.get('/api/v1/payment-records/', { params }),
  create: (data) => api.post('/api/v1/payment-records/', data),
}

// Digital Item Service
export const digitalItemService = {
  getAll: (params) => api.get('/api/v1/digital-items/', { params }),
  getById: (id) => api.get(`/api/v1/digital-items/${id}/`),
  create: (data) => api.post('/api/v1/digital-items/', data),
  getMyItems: () => api.get('/api/v1/digital-items/my_items/'),
}

// Merch Service
export const merchService = {
  getAll: (params) => api.get('/api/v1/merch/', { params }),
  getById: (id) => api.get(`/api/v1/merch/${id}/`),
  create: (data) => api.post('/api/v1/merch/', data),
  getMyItems: () => api.get('/api/v1/merch/my_items/'),
}

// Purchase Service
export const purchaseService = {
  getAll: (params) => api.get('/api/v1/purchases/', { params }),
  getMyPurchases: () => api.get('/api/v1/purchases/my_purchases/'),
}

// Upgrade Request Service
export const upgradeRequestService = {
  getAll: (params) => api.get('/api/v1/upgrade-requests/', { params }),
  create: (data) => api.post('/api/v1/upgrade-requests/', data),
}

// Verification Request Service
export const verificationRequestService = {
  getAll: (params) => api.get('/api/v1/verification-requests/', { params }),
  create: (data) => api.post('/api/v1/verification-requests/', data),
}

// Job Service
export const jobService = {
  getAll: (params) => api.get('/api/v1/jobs/', { params }),
  getById: (id) => api.get(`/api/v1/jobs/${id}/`),
  create: (data) => api.post('/api/v1/jobs/', data),
  getMyJobs: () => api.get('/api/v1/jobs/my_jobs/'),
}

// External Job Service
export const externalJobService = {
  getAll: (params) => api.get('/api/v1/external-jobs/', { params }),
  getById: (id) => api.get(`/api/v1/external-jobs/${id}/`),
  create: (data) => api.post('/api/v1/external-jobs/', data),
}

// Notification Service
export const notificationService = {
  getAll: () => api.get('/api/v1/notifications/'),
  getUnread: () => api.get('/api/v1/notifications/unread/'),
  markAsRead: (id) => api.post(`/api/v1/notifications/${id}/mark_read/`),
  markAllAsRead: () => api.post('/api/v1/notifications/mark_all_read/'),
}

// Feedback Service
export const feedbackService = {
  create: (data) => api.post('/api/v1/feedback/', data),
  getAll: (params) => api.get('/api/v1/feedback/', { params }),
}

// FAQ Service
export const faqService = {
  getAll: (params) => api.get('/api/v1/faqs/', { params }),
  getById: (id) => api.get(`/api/v1/faqs/${id}/`),
}

// Top Expert Service
export const topExpertService = {
  getAll: () => api.get('/api/v1/top-experts/'),
}

// Featured Content Service
export const featuredContentService = {
  getAll: (params) => api.get('/api/v1/featured-content/', { params }),
}

// Homepage Service
export const homepageService = {
  getData: () => api.get('/api/v1/homepage/'),
}
