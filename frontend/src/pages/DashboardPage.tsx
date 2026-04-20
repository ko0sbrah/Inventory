import { Link } from 'react-router-dom';
import { useDashboardMetrics } from '../hooks/useDashboard';
import Card from '../components/ui/Card';

const DashboardPage = () => {
  const { data, isLoading, error } = useDashboardMetrics();

  if (isLoading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  if (error || !data) {
    return <div className="text-red-600">Error loading dashboard</div>;
  }

  const stats = [
    { label: 'Total Items', value: data.total_items, color: 'blue' },
    { label: 'Low Stock', value: data.low_stock_items, color: 'yellow' },
    { label: 'Out of Stock', value: data.out_of_stock_items, color: 'red' },
    { label: "Today's Transactions", value: data.total_transactions_today, color: 'green' },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <p className="text-sm text-gray-500">{stat.label}</p>
            <p className={`text-3xl font-bold text-${stat.color}-600`}>{stat.value}</p>
          </Card>
        ))}
      </div>

      {/* Recent Transactions */}
      <Card title="Recent Transactions">
        {data.recent_transactions.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No recent transactions</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Item</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Change</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">After</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {data.recent_transactions.map((tx) => (
                  <tr key={tx.id}>
                    <td className="px-4 py-2 text-sm text-gray-900">Item #{tx.item_id.slice(0, 8)}</td>
                    <td className="px-4 py-2">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        tx.transaction_type === 'IN' ? 'bg-green-100 text-green-800' :
                        tx.transaction_type === 'OUT' ? 'bg-red-100 text-red-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {tx.transaction_type}
                      </span>
                    </td>
                    <td className={`px-4 py-2 text-sm ${tx.quantity_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {tx.quantity_change >= 0 ? '+' : ''}{tx.quantity_change}
                    </td>
                    <td className="px-4 py-2 text-sm text-gray-900">{tx.quantity_after}</td>
                    <td className="px-4 py-2 text-sm text-gray-500">
                      {new Date(tx.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="mt-4 text-center">
          <Link to="/transactions" className="text-blue-600 hover:underline text-sm">
            View all transactions →
          </Link>
        </div>
      </Card>
    </div>
  );
};

export default DashboardPage;
