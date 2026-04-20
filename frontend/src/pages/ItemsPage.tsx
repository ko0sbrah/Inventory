import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useItems, useDeleteItem } from '../hooks/useItems';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';

const ItemsPage = () => {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [lowStockOnly, setLowStockOnly] = useState(false);
  
  const { data, isLoading, error } = useItems({ search, page, page_size: 20, low_stock_only: lowStockOnly });
  const deleteMutation = useDeleteItem();

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this item?')) {
      await deleteMutation.mutateAsync(id);
    }
  };

  if (isLoading) return <div>Loading...</div>;
  if (error || !data) return <div className="text-red-600">Error loading items</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Inventory Items</h1>
        <Link to="/items/new">
          <Button>Add Item</Button>
        </Link>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex gap-4 flex-wrap">
          <div className="flex-1 min-w-64">
            <Input
              placeholder="Search items..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            />
          </div>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={lowStockOnly}
              onChange={(e) => { setLowStockOnly(e.target.checked); setPage(1); }}
              className="rounded"
            />
            <span>Low Stock Only</span>
          </label>
        </div>
      </Card>

      {/* Items Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">SKU</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Unit</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {data.items.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                    No items found
                  </td>
                </tr>
              ) : (
                data.items.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{item.name}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{item.sku || '-'}</td>
                    <td className="px-4 py-3 text-sm">
                      <span className={item.quantity <= item.low_stock_threshold ? 'text-red-600 font-medium' : 'text-gray-900'}>
                        {item.quantity}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">{item.unit}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        item.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {item.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <div className="flex gap-2">
                        <Link to={`/items/${item.id}`} className="text-blue-600 hover:underline">View</Link>
                        <button onClick={() => handleDelete(item.id)} className="text-red-600 hover:underline">Delete</button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {data.pages > 1 && (
          <div className="flex justify-center gap-2 mt-4">
            <Button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Previous</Button>
            <span className="px-4 py-2">Page {page} of {data.pages}</span>
            <Button onClick={() => setPage(p => Math.min(data.pages, p + 1))} disabled={page === data.pages}>Next</Button>
          </div>
        )}
      </Card>
    </div>
  );
};

export default ItemsPage;
