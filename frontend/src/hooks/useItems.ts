import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { itemsApi, InventoryItem, InventoryItemCreate, InventoryItemUpdate, TransactionCreate } from '@/api/items';

export function useItems(params?: {
  search?: string;
  category_id?: string;
  low_stock_only?: boolean;
  page?: number;
  page_size?: number;
}) {
  return useQuery({
    queryKey: ['items', params],
    queryFn: () => itemsApi.getItems(params),
  });
}

export function useItem(id: string) {
  return useQuery({
    queryKey: ['item', id],
    queryFn: () => itemsApi.getItem(id),
    enabled: !!id,
  });
}

export function useCreateItem() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: InventoryItemCreate) => itemsApi.createItem(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
    },
  });
}

export function useUpdateItem() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: InventoryItemUpdate }) =>
      itemsApi.updateItem(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      queryClient.invalidateQueries({ queryKey: ['item', id] });
    },
  });
}

export function useDeleteItem() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => itemsApi.deleteItem(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
    },
  });
}

export function useCreateTransaction() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ itemId, data }: { itemId: string; data: TransactionCreate }) =>
      itemsApi.createTransaction(itemId, data),
    onSuccess: (_, { itemId }) => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      queryClient.invalidateQueries({ queryKey: ['item', itemId] });
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function useItemTransactions(itemId: string, page?: number, page_size?: number) {
  return useQuery({
    queryKey: ['item-transactions', itemId, page, page_size],
    queryFn: () => itemsApi.getItemTransactions(itemId, page, page_size),
    enabled: !!itemId,
  });
}
