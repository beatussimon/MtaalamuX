import axios from 'axios'
import { useAuthStore } from '../store'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('auth-storage')
        const { token } = JSON.parse(refreshToken || '{}')?.state || {}

        if (token) {
          const response = await axios.post('/api/v1/auth/refresh/', {
            refresh: token,
          })

          const { access } = response.data
          useAuthStore.getState().setToken(access)
          originalRequest.headers.Authorization = `Bearer ${access}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        useAuthStore.getState().logout()
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api

// API service functions
export const authService = {
  login: (credentials) => api.post('/api/v1/auth/login/', credentials),
  register: (userData) => api.post('/api/v1/auth/register/', userData),
  refreshToken: (refresh) => api.post('/api/v1/auth/refresh/', { refresh }),
}

export const userService = {
  getCurrentUser: () => api.get('/api/v1/users/me/'),
  updateProfile: (data) => api.put('/api/v1/users/update_profile/', data),
}

export const categoryService = {
  getAll: () => api.get('/api/v1/categories/'),
  getWithProfessionals: () => api.get('/api/v1/categories/with_professionals/'),
}

export const professionalService = {
  getAll: (params) => api.get('/api/v1/professionals/', { params }),
  getById: (id) => api.get(`/api/v1/professionals/${id}/`),
  follow: (id) => api.post(`/api/v1/professionals/${id}/follow/`),
  getArticles: (id) => api.get(`/api/v1/professionals/${id}/articles/`),
  getReviews: (id) => api.get(`/api/v1/professionals/${id}/reviews/`),
  getPortfolio: (id) => api.get(`/api/v1/professionals/${id}/portfolio/`),
}

export const articleService = {
  getAll: (params) => api.get('/api/v1/articles/', { params }),
  getById: (id) => api.get(`/api/v1/articles/${id}/`),
  create: (data) => api.post('/api/v1/articles/', data),
  like: (id) => api.post(`/api/v1/articles/${id}/like/`),
  share: (id) => api.post(`/api/v1/articles/${id}/share/`),
  getComments: (id) => api.get(`/api/v1/articles/${id}/comments/`),
}

export const jobService = {
  getAll: (params) => api.get('/api/v1/jobs/', { params }),
  getById: (id) => api.get(`/api/v1/jobs/${id}/`),
  create: (data) => api.post('/api/v1/jobs/', data),
  getMyJobs: () => api.get('/api/v1/jobs/my_jobs/'),
}

export const externalJobService = {
  getAll: (params) => api.get('/api/v1/external-jobs/', { params }),
  getById: (id) => api.get(`/api/v1/external-jobs/${id}/`),
  create: (data) => api.post('/api/v1/external-jobs/', data),
}

export const notificationService = {
  getAll: () => api.get('/api/v1/notifications/'),
  getUnread: () => api.get('/api/v1/notifications/unread/'),
  markAsRead: (id) => api.post(`/api/v1/notifications/${id}/mark_read/`),
  markAllAsRead: () => api.post('/api/v1/notifications/mark_all_read/'),
}

export const messageService = {
  getInbox: () => api.get('/api/v1/messages/inbox/'),
  getSent: () => api.get('/api/v1/messages/sent/'),
  getConversation: (userId) => api.get('/api/v1/messages/conversation/', { params: { user_id: userId } }),
  send: (data) => api.post('/api/v1/messages/', data),
  markAsRead: (id) => api.post(`/api/v1/messages/${id}/mark_read/`),
  markAllAsRead: () => api.post('/api/v1/messages/mark_all_read/'),
}

export const feedbackService = {
  create: (data) => api.post('/api/v1/feedback/', data),
  getAll: (params) => api.get('/api/v1/feedback/', { params }),
}
