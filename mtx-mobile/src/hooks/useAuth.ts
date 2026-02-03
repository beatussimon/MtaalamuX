import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import { useAuthStore } from '../store';
import type { LoginCredentials, RegisterData, UserProfile } from '../types/api';

export function useLogin() {
  const setUser = useAuthStore((state) => state.setUser);
  const setProfile = useAuthStore((state) => state.setProfile);
  const setLoading = useAuthStore((state) => state.setLoading);
  
  return useMutation({
    mutationFn: async (credentials: LoginCredentials) => {
      setLoading(true);
      return api.login(credentials.username, credentials.password);
    },
    onSuccess: (data) => {
      setUser(data.user);
      // Fetch user profile
      api.getCurrentUser().then((profile) => {
        setProfile(profile as unknown as UserProfile);
      }).catch(console.error);
    },
    onError: (error: Error) => {
      setLoading(false);
      throw error;
    },
    onSettled: () => {
      setLoading(false);
    },
  });
}

export function useRegister() {
  const setUser = useAuthStore((state) => state.setUser);
  const setProfile = useAuthStore((state) => state.setProfile);
  const setLoading = useAuthStore((state) => state.setLoading);
  
  return useMutation({
    mutationFn: async (data: RegisterData) => {
      setLoading(true);
      return api.register(data);
    },
    onSuccess: (data) => {
      setUser(data.user);
      api.getCurrentUser().then((profile) => {
        setProfile(profile as unknown as UserProfile);
      }).catch(console.error);
    },
    onError: (error: Error) => {
      setLoading(false);
      throw error;
    },
    onSettled: () => {
      setLoading(false);
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  const logoutStore = useAuthStore((state) => state.logout);
  
  return useMutation({
    mutationFn: async () => {
      await api.logout();
    },
    onSuccess: () => {
      logoutStore();
      queryClient.clear();
    },
    onError: (error: Error) => {
      // Even on error, clear local state
      logoutStore();
      queryClient.clear();
      throw error;
    },
  });
}

export function useCurrentUser() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  
  return useQuery({
    queryKey: ['currentUser'],
    queryFn: () => api.getCurrentUser(),
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useTierInfo() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const setTier = useAuthStore((state) => state.setTier);
  
  return useQuery({
    queryKey: ['tierInfo'],
    queryFn: async () => {
      const data = await api.getTierInfo();
      setTier(data.tier);
      return data;
    },
    enabled: isAuthenticated,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  const setProfile = useAuthStore((state) => state.setProfile);
  
  return useMutation({
    mutationFn: async (data: {
      bio?: string;
      avatar?: string;
      interests?: string;
      theme?: 'light' | 'dark';
    }) => {
      return api.updateProfile(data);
    },
    onSuccess: (data) => {
      setProfile(data as unknown as UserProfile);
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
    },
  });
}
