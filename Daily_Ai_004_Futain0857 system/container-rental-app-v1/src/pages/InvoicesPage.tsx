import React, { useState, useEffect } from 'react';
import { Invoice } from '../types/invoice';
import { fetchInvoices, createInvoice } from '../services/api/invoicesApi';
import { createPayment, voidPayment } from '../services/api/paymentsApi';

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [selectedInvoiceId, setSelectedInvoiceId] = useState('');
  const [payAmount, setPayAmount] = useState('10000');
  const [payMethod, setPayMethod] = useState<'cash' | 'bank_transfer' | 'line_pay' | 'check'>('bank_transfer');

  const [newCustId, setNewCustId] = useState('');
  const [newAmountDue, setNewAmountDue] = useState('24000');

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchInvoices();
      setInvoices(data);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : '載入帳單失敗');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadData();
  }, []);

  const handleCreateInvoice = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createInvoice({
        customer_id: newCustId,
        invoice_type: 'rent',
        due_date: new Date().toISOString().split('T')[0],
        amount_due: Number(newAmountDue)
      });
      alert('應收帳單建立成功');
      void loadData();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : '建立失敗');
    }
  };

  const handleRecordPayment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedInvoiceId) {
      alert('請先選擇帳單');
      return;
    }
    const inv = invoices.find((i) => i.invoice_id === selectedInvoiceId);
    if (!inv) return;

    try {
      await createPayment({
        invoice_id: selectedInvoiceId,
        customer_id: inv.customer_id,
        payment_type: 'rent',
        payment_method: payMethod,
        payment_date: new Date().toISOString().split('T')[0],
        amount: Number(payAmount)
      });
      alert('收款成功紀錄！');
      void loadData();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : '收款失敗');
    }
  };

  const handleVoid = async (paymentId: string) => {
    try {
      await voidPayment(paymentId, '人工作廢');
      alert('付款紀錄已作廢');
      void loadData();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : '作廢失敗');
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6 text-slate-100">
      <h1 className="text-2xl font-bold">應收與收款管理 (Invoices & Payments)</h1>
      {error && <div className="p-3 bg-rose-900/50 text-rose-200 rounded">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <form onSubmit={handleCreateInvoice} className="p-4 bg-slate-900 rounded-lg space-y-4 border border-slate-800">
          <h2 className="text-lg font-semibold">1. 建立開立應收帳單</h2>
          <input
            type="text"
            placeholder="客戶 ID (e.g. CUST-001)"
            value={newCustId}
            onChange={(e) => setNewCustId(e.target.value)}
            className="w-full p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
            required
          />
          <input
            type="number"
            placeholder="應收金額 (e.g. 24000)"
            value={newAmountDue}
            onChange={(e) => setNewAmountDue(e.target.value)}
            className="w-full p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
            required
          />
          <button type="submit" className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded text-white font-medium">
            建立帳單
          </button>
        </form>

        <form onSubmit={handleRecordPayment} className="p-4 bg-slate-900 rounded-lg space-y-4 border border-slate-800">
          <h2 className="text-lg font-semibold">2. 登記收款 (部分 / 全額)</h2>
          <select
            value={selectedInvoiceId}
            onChange={(e) => setSelectedInvoiceId(e.target.value)}
            className="w-full p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
          >
            <option value="">-- 請選擇欲繳款帳單 --</option>
            {invoices.map((inv) => (
              <option key={inv.invoice_id} value={inv.invoice_id}>
                {inv.invoice_no} | 應收:${inv.amount_due} | 餘額:${inv.balance_due} ({inv.status})
              </option>
            ))}
          </select>

          <input
            type="number"
            placeholder="實收金額"
            value={payAmount}
            onChange={(e) => setPayAmount(e.target.value)}
            className="w-full p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
            required
          />

          <select
            value={payMethod}
            onChange={(e) => setPayMethod(e.target.value as 'cash' | 'bank_transfer' | 'line_pay' | 'check')}
            className="w-full p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
          >
            <option value="bank_transfer">銀行轉帳</option>
            <option value="cash">現金支付</option>
            <option value="line_pay">LINE Pay</option>
          </select>

          <button type="submit" className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded text-white font-medium">
            登記入帳
          </button>
        </form>
      </div>

      <div className="bg-slate-900 rounded-lg border border-slate-800 p-4">
        <h2 className="text-lg font-semibold mb-3">帳單列表與狀態追蹤</h2>
        {loading ? (
          <div>載入中...</div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="p-2">帳單單號</th>
                <th className="p-2">客戶 ID</th>
                <th className="p-2">應收金額</th>
                <th className="p-2">已付金額</th>
                <th className="p-2">剩餘未付</th>
                <th className="p-2">狀態</th>
                <th className="p-2">操作</th>
              </tr>
            </thead>
            <tbody>
              {invoices.map((inv) => (
                <tr key={inv.invoice_id} className="border-b border-slate-800/50">
                  <td className="p-2 font-mono text-xs text-amber-400">{inv.invoice_no}</td>
                  <td className="p-2">{inv.customer_id}</td>
                  <td className="p-2">${inv.amount_due.toLocaleString()}</td>
                  <td className="p-2 text-emerald-400">${inv.amount_paid.toLocaleString()}</td>
                  <td className="p-2 text-rose-400">${inv.balance_due.toLocaleString()}</td>
                  <td className="p-2">
                    <span
                      className={`px-2 py-0.5 text-xs rounded font-bold ${
                        inv.status === 'paid'
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                          : inv.status === 'partial'
                          ? 'bg-amber-950 text-amber-300 border border-amber-700'
                          : 'bg-rose-950 text-rose-300 border border-rose-700'
                      }`}
                    >
                      {inv.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="p-2">
                    <button
                      onClick={() => void handleVoid('PAY-TEST')}
                      className="px-2 py-1 text-xs bg-slate-800 hover:bg-slate-700 rounded text-slate-300"
                    >
                      作廢最近付款
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
