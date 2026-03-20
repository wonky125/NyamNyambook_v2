import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../lib/api';
import type { RecipeDetail, RecipeSummary, ScrapeResult, Tag } from '../types';

export function useRecipes(params?: { tag_id?: number; source_type?: string }) {
  return useQuery({
    queryKey: ['recipes', params],
    queryFn: async () => {
      const { data } = await api.get('/recipes', { params: { page: 1, per_page: 50, ...params } });
      return data.items as RecipeSummary[];
    },
  });
}

export function useRecipe(id: number) {
  return useQuery({
    queryKey: ['recipe', id],
    queryFn: async () => {
      const { data } = await api.get(`/recipes/${id}`);
      return data as RecipeDetail;
    },
  });
}

export function useCreateRecipe() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: object) => api.post('/recipes', body).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['recipes'] }),
  });
}

export function useUpdateRecipe(id: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: object) => api.put(`/recipes/${id}`, body).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['recipes'] });
      qc.invalidateQueries({ queryKey: ['recipe', id] });
    },
  });
}

export function useDeleteRecipe() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.delete(`/recipes/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['recipes'] }),
  });
}

export function useMarkCooked() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.post(`/recipes/${id}/cook`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['recipes'] }),
  });
}

export function useSearch(query: string) {
  return useQuery({
    queryKey: ['search', query],
    queryFn: async () => {
      const { data } = await api.get('/search', { params: { q: query } });
      return data as RecipeSummary[];
    },
    enabled: query.trim().length > 0,
  });
}

export function useScrape() {
  return useMutation({
    mutationFn: (url: string) => api.post('/scrape', { url }).then(r => r.data as ScrapeResult),
  });
}

export function useTags() {
  return useQuery({
    queryKey: ['tags'],
    queryFn: async () => {
      const { data } = await api.get('/tags');
      return data as Tag[];
    },
  });
}

export function useUploadImage() {
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      const { data } = await api.post('/images', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return data.url as string;
    },
  });
}
