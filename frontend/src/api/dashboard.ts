import apiClient from './client';

export interface DashboardMetrics {
  total_items: number;
  total_categories: number;
  low_stock_items: number;
  out_of_stock_items: number;
  total_transactions_today: number;
  recent_transactions: Transaction[];
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

export interface AuditLog {
  id: string;
  user_id: string | null;
  item_id: string | null;
  action: string;
  entity_type: string;
  entity_id: string;
  old_values: Record<string, unknown> | null;
  new_values: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

export const dashboardApi = {
  getMetrics: async (): Promise<DashboardMetrics> => {
    const response = await apiClient.get('/dashboard/metrics');
    return response.data;
  },

  getTransactions: async (params?: {
    item_id?: string;
    transaction_type?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }): Promise<{ transactions: Transaction[]; total: number; page: number; page_size: number; pages: number }> => {
    const response = await apiClient.get('/transactions', { params });
    return response.data;
  },

  getAuditLogs: async (params?: {
    user_id?: string;
    item_id?: string;
    entity_type?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }): Promise<{ logs: AuditLog[]; total: number; page: number; page_size: number; pages: number }> => {
    const response = await apiClient.get('/audit-logs', { params });
    return response.data;
  },
};

export const exportApi = {
  exportItemsCsv: async (params?: {
    search?: string;
    category_id?: string;
    low_stock_only?: boolean;
  }): Promise<Blob> => {
    const response = await apiClient.get('/export/items/csv', {
      params,
      responseType: 'blob',
    });
    return response.data;
  },
};
