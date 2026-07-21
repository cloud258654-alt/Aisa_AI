import React, { useState, useEffect } from 'react';
import { RatePlan } from '../types/ratePlan';
import { fetchRatePlans, createRatePlan } from '../services/api/ratePlansApi';

export default function RatePlansPage() {
  const [plans, setPlans] = useState<RatePlan[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [name, setName] = useState('');
  const [price, setPrice] = useState('3000');
  const [deposit, setDeposit] = useState('5000');

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchRatePlans();
      setPlans(data);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : '載入失敗');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadData();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createRatePlan({
        name,
        container_size_ft: 20,
        container_type: 'standard',
        billing_cycle: 'monthly',
        contract_months: 12,
        standard_monthly_price: Number(price),
        contract_price: Number(price) * 12,
        installment_count: 12,
        default_deposit: Number(deposit),
        first_year_discount: 0,
        active: true
      });
      setName('');
      void loadData();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : '建立失敗');
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6 text-slate-100">
      <h1 className="text-2xl font-bold">商品與費率方案管理 (Rate Plans)</h1>
      {error && <div className="p-3 bg-rose-900/50 text-rose-200 rounded">{error}</div>}

      <form onSubmit={handleCreate} className="p-4 bg-slate-900 rounded-lg space-y-4 border border-slate-800">
        <h2 className="text-lg font-semibold">新增費率方案</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            placeholder="方案名稱"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
            required
          />
          <input
            type="number"
            placeholder="標準月租金"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            className="p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
            required
          />
          <input
            type="number"
            placeholder="預設押金"
            value={deposit}
            onChange={(e) => setDeposit(e.target.value)}
            className="p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
            required
          />
        </div>
        <button type="submit" className="px-4 py-2 bg-amber-600 hover:bg-amber-500 rounded text-white font-medium">
          新增方案
        </button>
      </form>

      <div className="bg-slate-900 rounded-lg border border-slate-800 p-4">
        {loading ? (
          <div>載入中...</div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="p-2">ID</th>
                <th className="p-2">方案名稱</th>
                <th className="p-2">月租金</th>
                <th className="p-2">預設押金</th>
                <th className="p-2">狀態</th>
              </tr>
            </thead>
            <tbody>
              {plans.map((p) => (
                <tr key={p.rate_plan_id} className="border-b border-slate-800/50">
                  <td className="p-2 font-mono text-xs text-slate-400">{p.rate_plan_id}</td>
                  <td className="p-2 font-medium">{p.name}</td>
                  <td className="p-2">${p.standard_monthly_price.toLocaleString()}</td>
                  <td className="p-2">${p.default_deposit.toLocaleString()}</td>
                  <td className="p-2">{p.active ? '啟用' : '停用'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
