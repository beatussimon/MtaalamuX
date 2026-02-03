import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';

export function useCategories() {
  return useQuery({
    queryKey: ['categories'],
    queryFn: () => api.getCategories(),
    staleTime: 30 * 60 * 1000,
  });
}

export function useProfessionals(params?: {
  category?: string;
  q?: string;
  verification?: string;
  featured?: boolean;
}) {
  return useQuery({
    queryKey: ['professionals', params],
    queryFn: () => api.getProfessionals(params),
    staleTime: 10 * 60 * 1000,
  });
}

export function useProfessional(id: number) {
  return useQuery({
    queryKey: ['professional', id],
    queryFn: () => api.getProfessional(id),
    enabled: !!id,
    staleTime: 10 * 60 * 1000,
  });
}

export function useFollowProfessional() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => api.followProfessional(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['professional', id] });
      queryClient.invalidateQueries({ queryKey: ['professionals'] });
    },
  });
}

export function useProfessionalArticles(id: number) {
  return useQuery({
    queryKey: ['professionalArticles', id],
    queryFn: () => api.getProfessionalArticles(id),
    enabled: !!id,
    staleTime: 10 * 60 * 1000,
  });
}

export function useProfessionalResearch(id: number) {
  return useQuery({
    queryKey: ['professionalResearch', id],
    queryFn: () => api.getProfessionalResearch(id),
    enabled: !!id,
    staleTime: 10 * 60 * 1000,
  });
}

export function useProfessionalAvailability(id: number, params?: {
  show_all?: boolean;
  include_booked?: boolean;
}) {
  return useQuery({
    queryKey: ['professionalAvailability', id, params],
    queryFn: () => api.getProfessionalAvailability(id, params),
    enabled: !!id,
    staleTime: 2 * 60 * 1000,
  });
}
