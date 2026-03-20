import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../lib/api';
import type { ShoppingItem } from '../types';

export function useShoppingItems() {
  return useQuery({
    queryKey: ['shopping'],
    queryFn: async () => {
      const { data } = await api.get('/shopping');
      return data as ShoppingItem[];
    },
  });
}

export function useAddShoppingItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (name: string) => api.post('/shopping', { name }).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['shopping'] }),
  });
}

export function useToggleShoppingItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, is_checked }: { id: number; is_checked: boolean }) =>
      api.patch(`/shopping/${id}`, { is_checked }).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['shopping'] }),
  });
}

export function useDeleteShoppingItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.delete(`/shopping/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['shopping'] }),
  });
}

export function useClearChecked() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.delete('/shopping'),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['shopping'] }),
  });
}
