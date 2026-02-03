import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';
import Constants from 'expo-constants';
import { STORAGE_KEYS, AUTH_ENDPOINTS } from '../utils/api-constants';
import type { ApiError } from '../types/api';

// API Configuration
const API_BASE_URL = Constants.expoConfig?.extra?.API_BASE_URL || process.env.API_BASE_URL || 'http://localhost:8000/api';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Token refresh state
let isRefreshing = false;
let failedRequestsQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: Error) => void;
}> = [];

/**
 * Get access token from secure storage
 */
async function getAccessToken(): Promise<string | null> {
  try {
    return await SecureStore.getItemAsync(STORAGE_KEYS.ACCESS_TOKEN);
  } catch {
    return null;
  }
}

/**
 * Get refresh token from secure storage
 */
async function getRefreshToken(): Promise<string | null> {
  try {
    return await SecureStore.getItemAsync(STORAGE_KEYS.REFRESH_TOKEN);
  } catch {
    return null;
  }
}

/**
 * Store tokens in secure storage
 */
async function storeTokens(accessToken: string, refreshToken: string): Promise<void> {
  await SecureStore.setItemAsync(STORAGE_KEYS.ACCESS_TOKEN, accessToken);
  await SecureStore.setItemAsync(STORAGE_KEYS.REFRESH_TOKEN, refreshToken);
}

/**
 * Clear tokens from secure storage
 */
async function clearTokens(): Promise<void> {
  await SecureStore.deleteItemAsync(STORAGE_KEYS.ACCESS_TOKEN);
  await SecureStore.deleteItemAsync(STORAGE_KEYS.REFRESH_TOKEN);
}

/**
 * Refresh access token
 */
async function refreshAccessToken(): Promise<string> {
  const refreshToken = await getRefreshToken();
  
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }
  
  const response = await axios.post(`${API_BASE_URL}${AUTH_ENDPOINTS.TOKEN_REFRESH}`, {
    refresh: refreshToken,
  });
  
  const { access } = response.data;
  
  // Store new access token
  await SecureStore.setItemAsync(STORAGE_KEYS.ACCESS_TOKEN, access);
  
  return access;
}

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    const token = await getAccessToken();
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors and token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config;
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401 && originalRequest) {
      // If already refreshing, queue the request
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedRequestsQueue.push({
            resolve: (token: string) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              resolve(apiClient(originalRequest));
            },
            reject: (err: Error) => {
              reject(err);
            },
          });
        });
      }
      
      isRefreshing = true;
      
      try {
        const newAccessToken = await refreshAccessToken();
        
        // Update Authorization header for original request
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        
        // Process queued requests
        failedRequestsQueue.forEach(({ resolve }) => resolve(newAccessToken));
        failedRequestsQueue = [];
        
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Clear queue with error
        failedRequestsQueue.forEach(({ reject }) => reject(refreshError as Error));
        failedRequestsQueue = [];
        
        // Clear tokens and redirect to login
        await clearTokens();
        
        // Check if we're not in a browser environment
        if (Platform.OS !== 'web') {
          // Use Expo Router for navigation
          const router = require('expo-router').router;
          router.replace('/(auth)/login');
        }
        
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
    
    // Handle other errors
    const errorMessage = error.response?.data?.detail || error.message || 'An error occurred';
    
    return Promise.reject(new Error(errorMessage));
  }
);

// Export API methods
export const api = {
  // Auth
  login: async (username: string, password: string) => {
    const response = await apiClient.post(AUTH_ENDPOINTS.LOGIN, { username, password });
    const { access, refresh, user } = response.data;
    await storeTokens(access, refresh);
    return { user, access, refresh };
  },
  
  register: async (data: {
    username: string;
    email: string;
    password: string;
    password2: string;
    first_name?: string;
    last_name?: string;
  }) => {
    const response = await apiClient.post(AUTH_ENDPOINTS.REGISTER, data);
    const { access, refresh, user } = response.data;
    await storeTokens(access, refresh);
    return { user, access, refresh };
  },
  
  logout: async () => {
    await clearTokens();
  },
  
  getCurrentUser: async () => {
    const response = await apiClient.get(AUTH_ENDPOINTS.USER_ME);
    return response.data;
  },
  
  getTierInfo: async () => {
    const response = await apiClient.get(AUTH_ENDPOINTS.TIER_INFO);
    return response.data;
  },
  
  updateProfile: async (data: {
    bio?: string;
    avatar?: string;
    interests?: string;
    theme?: 'light' | 'dark';
  }) => {
    const response = await apiClient.put(AUTH_ENDPOINTS.UPDATE_PROFILE, data);
    return response.data;
  },
  
  // Categories
  getCategories: async () => {
    const response = await apiClient.get('/categories/');
    return response.data;
  },
  
  // Professionals
  getProfessionals: async (params?: {
    category?: string;
    q?: string;
    verification?: string;
    featured?: boolean;
  }) => {
    const response = await apiClient.get('/professionals/', { params });
    return response.data;
  },
  
  getProfessional: async (id: number) => {
    const response = await apiClient.get(`/professionals/${id}/`);
    return response.data;
  },
  
  followProfessional: async (id: number) => {
    const response = await apiClient.post(`/professionals/${id}/follow/`);
    return response.data;
  },
  
  getProfessionalArticles: async (id: number) => {
    const response = await apiClient.get(`/professionals/${id}/articles/`);
    return response.data;
  },
  
  getProfessionalResearch: async (id: number) => {
    const response = await apiClient.get(`/professionals/${id}/research/`);
    return response.data;
  },
  
  getProfessionalAvailability: async (id: number, params?: {
    show_all?: boolean;
    include_booked?: boolean;
  }) => {
    const response = await apiClient.get(`/professionals/${id}/availability/`, { params });
    return response.data;
  },
  
  // Conversations
  getConversations: async () => {
    const response = await apiClient.get('/conversations/');
    return response.data;
  },
  
  getConversation: async (id: number) => {
    const response = await apiClient.get(`/conversations/${id}/`);
    return response.data;
  },
  
  // Messages
  getMessages: async (conversationId: number) => {
    const response = await apiClient.get(`/conversations/${conversationId}/messages/`);
    return response.data;
  },
  
  sendMessage: async (conversationId: number, data: {
    content: string;
    file?: unknown;
    image?: unknown;
    parent?: number;
  }) => {
    const response = await apiClient.post(`/conversations/${conversationId}/messages/`, data);
    return response.data;
  },
  
  initiateConversation: async (expertId: number) => {
    const response = await apiClient.post('/messages/initiate/', { expert_id: expertId });
    return response.data;
  },
  
  // Articles
  getArticles: async (params?: { category?: number; is_featured?: boolean }) => {
    const response = await apiClient.get('/articles/', { params });
    return response.data;
  },
  
  getArticle: async (id: number) => {
    const response = await apiClient.get(`/articles/${id}/`);
    return response.data;
  },
  
  likeArticle: async (id: number) => {
    const response = await apiClient.post(`/articles/${id}/like/`);
    return response.data;
  },
  
  // Research
  getResearch: async (params?: { category?: number; status?: string }) => {
    const response = await apiClient.get('/research/', { params });
    return response.data;
  },
  
  getResearchDetail: async (id: number) => {
    const response = await apiClient.get(`/research/${id}/`);
    return response.data;
  },
  
  likeResearch: async (id: number) => {
    const response = await apiClient.post(`/research/${id}/like/`);
    return response.data;
  },
};

export default apiClient;
