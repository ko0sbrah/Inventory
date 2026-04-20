import apiClient from './client';

export interface InventoryItem {
  id: string;
  name: string;
  sku: string | null;
  category_id: string | null;
  quantity: number;
  unit: string;
  low_stock_threshold: number;
  description: string | null;
  price: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface InventoryItemCreate {
  name: string;
  sku?: string;
  category_id?: string;
  quantity?: number;
  unit?: string;
  low_stock_threshold?: number;
  description?: string;
  price?: number;
}

export interface InventoryItemUpdate {
  name?: string;
  sku?: string;
  category_id?: string;
  unit?: string;
  low_stock_threshold?: number;
  description?: string;
  price?: number;
  is_active?: boolean;
}

export interface Transaction {
  id: string;
  item_id: string;
  user_id: string | null;
  transaction_type: 'IN' | 'OUT' | 'ADJUSTMENT';
  quantity_change: number;
  quantity_before: number;
  quantity_after: number;
  reference: string | null;
  notes: string | null;
  created_at: string;
}

export interface TransactionCreate {
  transaction_type: 'IN' | 'OUT' | 'ADJUSTMENT';
  quantity_change: number;
  reference?: string;
  notes?: string;
}

export interface PaginatedResponse<T> {
  items: T[] | transactions: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export const itemsApi = {
  getItems: async (params?: {
    search?: string;
    category_id?: string;
    low_stock_only?: boolean;
    page?: number;
    page_size?: number;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
  }): Promise<PaginatedResponse<InventoryItem>> => {
    const response = await apiClient.get('/items', { params });
    return response.data;
  },

  getItem: async (id: string): Promise<InventoryItem> => {
    const response = await apiClient.get(`/items/${id}`);
    return response.data;
  },

  createItem: async (data: InventoryItemCreate): Promise<InventoryItem> => {
    const response = await apiClient.post('/items', data);
    return response.data;
  },

  updateItem: async (id: string, data: InventoryItemUpdate): Promise<InventoryItem> => {
    const response = await apiClient.put(`/items/${id}`, data);
    return response.data;
  },

  deleteItem: async (id: string): Promise<{ message: string }> => {
    const response = await apiClient.delete(`/items/${id}`);
    return response.data;
  },

  createTransaction: async (itemId: string, data: TransactionCreate): Promise<Transaction> => {
    const response = await apiClient.post(`/items/${itemId}/transactions`, data);
    return response.data;
  },

  getItemTransactions: async (
    itemId: string,
    page?: number,
    page_size?: number
  ): Promise<PaginatedResponse<Transaction>> => {
    const response = await apiClient.get(`/items/${itemId}/transactions`, {
      params: { page, page_size },
    });
    return response.data;
  },
};
