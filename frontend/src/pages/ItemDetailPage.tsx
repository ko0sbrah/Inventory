import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useItem, useCreateTransaction } from '../hooks/useItems';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';

const ItemDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: item, isLoading } = useItem(id!);
  const createTransaction = useCreateTransaction();
  
  const [showTransaction, setShowTransaction] = useState(false);
  const [txData, setTxData] = useState({
    transaction_type: 'IN' as 'IN' | 'OUT' | 'ADJUSTMENT',
    quantity_change: 0,
    reference: '',
    notes: '',
  });

  if (isLoading) return <div>Loading...</div>;
  if (!item) return <div className="text-red-600">Item not found</div>;

  const handleTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createTransaction.mutateAsync({ itemId: id!, data: txData });
      setShowTransaction(false);
      setTxData({ transaction_type: 'IN', quantity_change: 0, reference: '', notes: '' });
    } catch (err) {
      alert('Transaction failed');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <Link to="/items" className="text-blue-600 hover:underline text-sm">← Back to Items</Link>
          <h1 className="text-2xl font-bold text-gray-800">{item.name}</h1>
        </div>
        <Button onClick={() => setShowTransaction(!showTransaction)}>
          {showTransaction ? 'Cancel' : 'Add Transaction'}
        </Button>
      </div>

      {showTransaction && (
        <Card title="Record Transaction">
          <form onSubmit={handleTransaction} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
              <select
                value={txData.transaction_type}
                onChange={(e) => setTxData({ ...txData, transaction_type: e.target.value as any })}
                className="w-full px-3 py-2 border rounded-lg"
              >
                <option value="IN">Stock In</option>
                <option value="OUT">Stock Out</option>
                <option value="ADJUSTMENT">Adjustment</option>
              </select>
            </div>
            <Input
              label="Quantity"
              type="number"
              value={txData.quantity_change}
              onChange={(e) => setTxData({ ...txData, quantity_change: parseInt(e.target.value) || 0 })}
              required
              min={1}
            />
            <Input
              label="Reference"
              value={txData.reference}
              onChange={(e) => setTxData({ ...txData, reference: e.target.value })}
            />
            <Input
              label="Notes"
              value={txData.notes}
              onChange={(e) => setTxData({ ...txData, notes: e.target.value })}
            />
            <Button type="submit">Submit Transaction</Button>
          </form>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title="Item Details">
          <dl className="space-y-3">
            <div><dt className="text-sm text-gray-500">SKU</dt><dd className="font-medium">{item.sku || 'N/A'}</dd></div>
            <div><dt className="text-sm text-gray-500">Current Quantity</dt><dd className={`font-medium ${item.quantity <= item.low_stock_threshold ? 'text-red-600' : ''}`}>{item.quantity} {item.unit}</dd></div>
            <div><dt className="text-sm text-gray-500">Low Stock Threshold</dt><dd className="font-medium">{item.low_stock_threshold} {item.unit}</dd></div>
            <div><dt className="text-sm text-gray-500">Price</dt><dd className="font-medium">${item.price?.toFixed(2) || 'N/A'}</dd></div>
            <div><dt className="text-sm text-gray-500">Status</dt><dd><span className={`px-2 py-1 text-xs rounded-full ${item.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>{item.is_active ? 'Active' : 'Inactive'}</span></dd></div>
            <div><dt className="text-sm text-gray-500">Created</dt><dd className="font-medium">{new Date(item.created_at).toLocaleDateString()}</dd></div>
            <div><dt className="text-sm text-gray-500">Last Updated</dt><dd className="font-medium">{new Date(item.updated_at).toLocaleDateString()}</dd></div>
          </dl>
        </Card>

        {item.description && (
          <Card title="Description">
            <p className="text-gray-700">{item.description}</p>
          </Card>
        )}
      </div>
    </div>
  );
};

export default ItemDetailPage;
