import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../services/api'

// Auth Store
export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      tierInfo: null, // { tier, display_tier, is_basic, is_professional, is_premium, can_initiate_consultation, can_post_content, can_sell_items }

      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setToken: (token) => {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        set({ token })
      },
      
      setRefreshToken: (refreshToken) => set({ refreshToken }),

      setTierInfo: (tierInfo) => set({ tierInfo }),

      login: async (credentials) => {
        set({ isLoading: true, error: null })
        try {
          const response = await api.post('/api/v1/auth/login/', credentials)
          const { access, refresh } = response.data
          api.defaults.headers.common['Authorization'] = `Bearer ${access}`
          
          // Store both tokens (refresh token is needed for token rotation)
          set({ 
            token: access, 
            refreshToken: refresh || null,
            isAuthenticated: true, 
            isLoading: false 
          })
          
          // Fetch user data
          const userResponse = await api.get('/api/v1/users/me/')
          set({ user: userResponse.data })
          
          // Fetch tier info
          try {
            const tierResponse = await api.get('/api/v1/users/tier_info/')
            set({ tierInfo: tierResponse.data })
          } catch (tierError) {
            console.error('Failed to fetch tier info:', tierError)
          }
          
          return { success: true }
        } catch (error) {
          const message = error.response?.data?.detail || 'Login failed'
          set({ error: message, isLoading: false })
          return { success: false, error: message }
        }
      },

      register: async (userData) => {
        set({ isLoading: true, error: null })
        try {
          const response = await api.post('/api/v1/auth/register/', userData)
          set({ isLoading: false })
          return { success: true, data: response.data }
        } catch (error) {
          const message = error.response?.data?.detail || 'Registration failed'
          set({ error: message, isLoading: false })
          return { success: false, error: message }
        }
      },

      logout: () => {
        delete api.defaults.headers.common['Authorization']
        set({ user: null, token: null, refreshToken: null, isAuthenticated: false, tierInfo: null })
      },

      checkAuth: async () => {
        const { token } = get()
        if (!token) return

        try {
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`
          const response = await api.get('/api/v1/users/me/')
          set({ user: response.data, isAuthenticated: true })
          
          // Fetch tier info
          try {
            const tierResponse = await api.get('/api/v1/users/tier_info/')
            set({ tierInfo: tierResponse.data })
          } catch (tierError) {
            console.error('Failed to fetch tier info:', tierError)
          }
        } catch (error) {
          get().logout()
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token, refreshToken: state.refreshToken }),
    }
  )
)

// Theme Store
export const useThemeStore = create(
  persist(
    (set, get) => ({
      theme: 'light',

      setTheme: (theme) => {
        document.documentElement.classList.remove('light', 'dark')
        document.documentElement.classList.add(theme)
        set({ theme })
      },

      toggleTheme: () => {
        const { theme } = get()
        const newTheme = theme === 'light' ? 'dark' : 'light'
        get().setTheme(newTheme)
      },

      initTheme: () => {
        const { theme } = get()
        document.documentElement.classList.add(theme)
      },
    }),
    {
      name: 'theme-storage',
    }
  )
)

// UI Store
export const useUIStore = create((set) => ({
  sidebarOpen: false,
  modalOpen: false,
  modalContent: null,

  openSidebar: () => set({ sidebarOpen: true }),
  closeSidebar: () => set({ sidebarOpen: false }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  openModal: (content) => set({ modalOpen: true, modalContent: content }),
  closeModal: () => set({ modalOpen: false, modalContent: null }),
}))

// Tier-aware helper functions
export const tierHelpers = {
  isBasic: (tierInfo) => tierInfo?.is_basic === true || tierInfo?.tier === 'basic',
  isProfessional: (tierInfo) => tierInfo?.is_professional === true || tierInfo?.tier === 'professional',
  isPremium: (tierInfo) => tierInfo?.is_premium === true || tierInfo?.tier === 'premium',
  canInitiateConsultation: (tierInfo) => tierInfo?.can_initiate_consultation === true || 
    ['professional', 'premium'].includes(tierInfo?.tier),
  canPostContent: (tierInfo) => tierInfo?.can_post_content === true || tierInfo?.tier === 'premium',
  canSellItems: (tierInfo) => tierInfo?.can_sell_items === true || tierInfo?.tier === 'premium',
  isVerified: (tierInfo) => tierInfo?.is_verified === true,
  getUpgradeCTA: (tierInfo) => {
    if (!tierInfo) return 'Upgrade'
    if (tierInfo.tier === 'basic') return 'Upgrade'
    if (tierInfo.tier === 'professional') return 'Premium'
    return null // Already premium
  },
  getDisplayTier: (tierInfo) => tierInfo?.display_tier || tierInfo?.tier?.charAt(0).toUpperCase() + tierInfo?.tier?.slice(1) || 'Basic',
  // Helper to check if user can access a feature based on tier
  canAccess: (tierInfo, feature) => {
    if (!tierInfo) return false
    switch (feature) {
      case 'consultation':
        return tierHelpers.canInitiateConsultation(tierInfo)
      case 'post_content':
        return tierHelpers.canPostContent(tierInfo)
      case 'sell_items':
        return tierHelpers.canSellItems(tierInfo)
      case 'messages':
        return tierHelpers.isProfessional(tierInfo)
      default:
        return false
    }
  },
}
