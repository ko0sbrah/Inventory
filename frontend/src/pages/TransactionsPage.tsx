import { useState } from 'react';
import { useTransactions } from '../hooks/useDashboard';
import Card from '../components/ui/Card';

const TransactionsPage = () => {
  const [page, setPage] = useState(1);
  const [transactionType, setTransactionType] = useState('');
  
  const { data, isLoading, error } = useTransactions({ page, page_size: 50, transaction_type: transactionType || undefined });

  if (isLoading) return <div>Loading...</div>;
  if (error || !data) return <div className="text-red-600">Error loading transactions</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Transactions</h1>

      <Card>
        <div className="flex gap-4 mb-4">
          <select
            value={transactionType}
            onChange={(e) => { setTransactionType(e.target.value); setPage(1); }}
            className="px-3 py-2 border rounded-lg"
          >
            <option value="">All Types</option>
            <option value="IN">Stock In</option>
            <option value="OUT">Stock Out</option>
            <option value="ADJUSTMENT">Adjustment</option>
          </select>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Change</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Before</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">After</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reference</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {data.transactions.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-gray-500">No transactions found</td>
                </tr>
              ) : (
                data.transactions.map((tx) => (
                  <tr key={tx.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-500">{tx.id.slice(0, 8)}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">Item #{tx.item_id.slice(0, 8)}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        tx.transaction_type === 'IN' ? 'bg-green-100 text-green-800' :
                        tx.transaction_type === 'OUT' ? 'bg-red-100 text-red-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {tx.transaction_type}
                      </span>
                    </td>
                    <td className={`px-4 py-3 text-sm font-medium ${tx.quantity_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {tx.quantity_change >= 0 ? '+' : ''}{tx.quantity_change}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">{tx.quantity_before}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{tx.quantity_after}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{tx.reference || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {new Date(tx.created_at).toLocaleString()}
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

export default TransactionsPage;
