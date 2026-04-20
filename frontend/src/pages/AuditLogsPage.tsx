import { useState } from 'react';
import { useAuditLogs } from '../hooks/useDashboard';
import Card from '../components/ui/Card';

const AuditLogsPage = () => {
  const [page, setPage] = useState(1);
  const { data, isLoading, error } = useAuditLogs({ page, page_size: 50 });

  if (isLoading) return <div>Loading...</div>;
  if (error || !data) return <div className="text-red-600">Error loading audit logs</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Audit Logs</h1>

      <Card>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Entity</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Entity Type</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {data.logs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-gray-500">No audit logs found</td>
                </tr>
              ) : (
                data.logs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-500">{log.id.slice(0, 8)}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">{log.action}</span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">{log.entity_id.slice(0, 8)}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{log.entity_type}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {data.pages > 1 && (
          <div className="flex justify-center gap-2 mt-4">
            <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-4 py-2 border rounded disabled:opacity-50">Previous</button>
            <span className="px-4 py-2">Page {page} of {data.pages}</span>
            <button onClick={() => setPage(p => Math.min(data.pages, p + 1))} disabled={page === data.pages} className="px-4 py-2 border rounded disabled:opacity-50">Next</button>
          </div>
        )}
      </Card>
    </div>
  );
};

export default AuditLogsPage;
