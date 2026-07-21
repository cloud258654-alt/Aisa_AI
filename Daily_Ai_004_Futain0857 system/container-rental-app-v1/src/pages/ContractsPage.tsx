import React, { useState, useEffect } from 'react';
import { Contract } from '../types/contract';
import { fetchContracts, createAndActivateContract, renewContract } from '../services/api/contractsApi';

export default function ContractsPage() {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [customerId, setCustomerId] = useState('');
  const [containerId1, setContainerId1] = useState('');
  const [containerId2, setContainerId2] = useState('');
  const [rentTotal, setRentTotal] = useState('48000');
  const [depositTotal, setDepositTotal] = useState('5000');
  const [installmentCount, setInstallmentCount] = useState('2');
  const [startDate, setStartDate] = useState('2026-08-01');

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchContracts();
      setContracts(data);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : '載入合約失敗');
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
      const items = [
        {
          container_id: containerId1,
          unit_price: Number(rentTotal),
          discount_amount: 0,
          effective_price: Number(rentTotal),
          start_date: startDate,
          status: 'active' as const
        }
      ];
      if (containerId2) {
        items.push({
          container_id: containerId2,
          unit_price: Number(rentTotal),
          discount_amount: 0,
          effective_price: Number(rentTotal),
          start_date: startDate,
          status: 'active' as const
        });
      }

      await createAndActivateContract({
        customer_id: customerId,
        start_date: startDate,
        rent_total: Number(rentTotal),
        deposit_total: Number(depositTotal),
        installment_count: Number(installmentCount),
        items
      });
      alert('合約建立與啟用成功！');
      void loadData();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : '建立失敗');
    }
  };

  const handleRenew = async (prevId: string) => {
    try {
      await renewContract({
        previous_contract_id: prevId,
        start_date: '2027-08-01',
        rent_total: 48000,
        deposit_total: 0,
        installment_count: 2,
        items: [
          {
            container_id: containerId1 || 'CONT-001',
            unit_price: 48000,
            discount_amount: 0,
            effective_price: 48000,
            start_date: '2027-08-01',
            status: 'active' as const
          }
        ]
      });
      alert('合約續約成功！');
      void loadData();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : '續約失敗');
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6 text-slate-100">
      <h1 className="text-2xl font-bold">合約管理 (Contracts Workflow)</h1>
      {error && <div className="p-3 bg-rose-900/50 text-rose-200 rounded">{error}</div>}

      <form onSubmit={handleCreate} className="p-4 bg-slate-900 rounded-lg space-y-4 border border-slate-800">
        <h2 className="text-lg font-semibold">建立並啟用新合約 (Wizard)</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            placeholder="客戶 ID (e.g. CUST-001)"
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value)}
            className="p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
            required
          />
          <input
            type="text"
            placeholder="貨櫃一 ID (e.g. CONT-001)"
            value={containerId1}
            onChange={(e) => setContainerId1(e.target.value)}
            className="p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
            required
          />
          <input
            type="text"
            placeholder="貨櫃二 ID (選填, 多櫃合約)"
            value={containerId2}
            onChange={(e) => setContainerId2(e.target.value)}
            className="p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
          />
          <input
            type="number"
            placeholder="租金總額"
            value={rentTotal}
            onChange={(e) => setRentTotal(e.target.value)}
            className="p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
            required
          />
          <input
            type="number"
            placeholder="押金金額"
            value={depositTotal}
            onChange={(e) => setDepositTotal(e.target.value)}
            className="p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
            required
          />
          <input
            type="number"
            placeholder="分期期數 (e.g. 2)"
            value={installmentCount}
            onChange={(e) => setInstallmentCount(e.target.value)}
            className="p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
            required
          />
          <input
            type="date"
            placeholder="起算日期"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
            required
          />
        </div>
        <button type="submit" className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded text-white font-medium">
          啟用合約
        </button>
      </form>

      <div className="bg-slate-900 rounded-lg border border-slate-800 p-4">
        {loading ? (
          <div>載入中...</div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="p-2">合約單號</th>
                <th className="p-2">客戶 ID</th>
                <th className="p-2">起算日</th>
                <th className="p-2">租金總額</th>
                <th className="p-2">押金</th>
                <th className="p-2">狀態</th>
                <th className="p-2">操作</th>
              </tr>
            </thead>
            <tbody>
              {contracts.map((c) => (
                <tr key={c.contract_id} className="border-b border-slate-800/50">
                  <td className="p-2 font-mono text-xs text-amber-400">{c.contract_no}</td>
                  <td className="p-2">{c.customer_id}</td>
                  <td className="p-2">{c.start_date}</td>
                  <td className="p-2">${c.rent_total.toLocaleString()}</td>
                  <td className="p-2">${c.deposit_total.toLocaleString()}</td>
                  <td className="p-2 font-semibold text-emerald-400">{c.status}</td>
                  <td className="p-2">
                    <button
                      onClick={() => void handleRenew(c.contract_id)}
                      className="px-2 py-1 text-xs bg-cyan-700 hover:bg-cyan-600 rounded text-white"
                    >
                      辦理續約
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
