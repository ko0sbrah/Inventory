import { useQuery } from '@tanstack/react-query';
import { dashboardApi, exportApi } from '@/api/dashboard';

export function useDashboardMetrics() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: () => dashboardApi.getMetrics(),
  });
}

export function useTransactions(params?: {
  item_id?: string;
  transaction_type?: string;
  start_date?: string;
  end_date?: string;
  page?: number;
  page_size?: number;
}) {
  return useQuery({
    queryKey: ['transactions', params],
    queryFn: () => dashboardApi.getTransactions(params),
  });
}

export function useAuditLogs(params?: {
  user_id?: string;
  item_id?: string;
  entity_type?: string;
  start_date?: string;
  end_date?: string;
  page?: number;
  page_size?: number;
}) {
  return useQuery({
    queryKey: ['audit-logs', params],
    queryFn: () => dashboardApi.getAuditLogs(params),
  });
}

export function useExportItems() {
  return useQuery({
    queryKey: ['export-items'],
    queryFn: (params?: { search?: string; category_id?: string; low_stock_only?: boolean }) =>
      exportApi.exportItemsCsv(params),
    enabled: false,
  });
}
