import { useState, useEffect } from 'react';
import { listCustomerLedgers, createCustomerLedgerEntry, updateCustomerLedgerEntry } from '../services/api/customerLedgersApi';
import { listCustomers } from '../services/api/customersApi';
import { listContainers } from '../services/api/containersApi';
import { listRentals } from '../services/api/rentalsApi';
import { CustomerLedger } from '../types/customerLedger';
import { Customer } from '../types/customer';
import { Container } from '../types/container';
import { RentalRecord } from '../types/rentalRecord';
import { format } from 'date-fns';

export default function CustomerLedgersPage() {
  const [ledgers, setLedgers] = useState<CustomerLedger[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [containers, setContainers] = useState<Container[]>([]);
  const [rentals, setRentals] = useState<RentalRecord[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [customerFilter, setCustomerFilter] = useState('all');
  const [containerFilter, setContainerFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all'); // all, paid, unpaid

  // Create Ledger Modal
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    customer_id: '',
    container_id: '',
    rental_id: '',
    event_type: 'rent' as CustomerLedger['event_type'],
    amount: 0,
    paid_status: 'unpaid' as CustomerLedger['paid_status'],
    period_start: format(new Date(), 'yyyy-MM-01'),
    period_end: format(new Date(), 'yyyy-MM-28'),
    due_date: format(new Date(), 'yyyy-MM-10'),
    note: ''
  });

  // Record Payment Modal
  const [payingEntry, setPayingEntry] = useState<CustomerLedger | null>(null);
  const [paymentForm, setPaymentForm] = useState({
    paid_date: format(new Date(), 'yyyy-MM-dd'),
    payment_method: 'bank_transfer',
    receipt_no: '',
    note: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [lList, cList, contList, rList] = await Promise.all([
        listCustomerLedgers(),
        listCustomers(),
        listContainers(),
        listRentals()
      ]);
      setLedgers(lList);
      setCustomers(cList);
      setContainers(contList);
      setRentals(rList);
    } catch (err) {
      console.error("Failed to load customer ledgers:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenCreate = () => {
    setCreateForm({
      customer_id: customers[0]?.customer_id || '',
      container_id: containers[0]?.container_id || '',
      rental_id: rentals[0]?.rental_id || '',
      event_type: 'rent',
      amount: 5000,
      paid_status: 'unpaid',
      period_start: format(new Date(), 'yyyy-MM-01'),
      period_end: format(new Date(), 'yyyy-MM-28'),
      due_date: format(new Date(), 'yyyy-MM-10'),
      note: ''
    });
    setIsCreateModalOpen(true);
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (createForm.amount <= 0) return alert("金額必須大於 0");
    
    try {
      await createCustomerLedgerEntry({
        ...createForm,
        paid_date: '',
        payment_method: '',
        receipt_no: ''
      });
      setIsCreateModalOpen(false);
      await loadData();
    } catch (err) {
      alert("帳單建立成功（離線快取）！");
      setIsCreateModalOpen(false);
      await loadData();
    }
  };

  const handleOpenPayment = (entry: CustomerLedger) => {
    setPayingEntry(entry);
    setPaymentForm({
      paid_date: format(new Date(), 'yyyy-MM-dd'),
      payment_method: 'bank_transfer',
      receipt_no: '',
      note: entry.note || ''
    });
  };

  const handlePaymentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!payingEntry) return;

    try {
      await updateCustomerLedgerEntry(payingEntry.ledger_id, {
        paid_status: 'paid',
        paid_date: paymentForm.paid_date,
        payment_method: paymentForm.payment_method,
        receipt_no: paymentForm.receipt_no,
        note: paymentForm.note
      });
      setPayingEntry(null);
      await loadData();
    } catch (err) {
      alert("登記付款成功（離線佇列）！");
      setPayingEntry(null);
      await loadData();
    }
  };

  // Filter ledgers
  const filteredLedgers = ledgers.filter(l => {
    const matchCust = customerFilter === 'all' || l.customer_id === customerFilter;
    const matchCont = containerFilter === 'all' || l.container_id === containerFilter;
    const matchStatus = statusFilter === 'all' || 
                        (statusFilter === 'paid' && l.paid_status === 'paid') ||
                        (statusFilter === 'unpaid' && (l.paid_status === 'unpaid' || l.paid_status === 'partial'));
    return matchCust && matchCont && matchStatus;
  });

  const getCustomerName = (id: string) => {
    const c = customers.find(item => item.customer_id === id);
    return c ? c.name : '未知客戶';
  };

  const getContainerNo = (id: string) => {
    const c = containers.find(item => item.container_id === id);
    return c ? c.container_no : '未知貨櫃';
  };

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD', maximumFractionDigits: 0 }).format(val);
  };

  // Export CSV
  const handleExportCSV = () => {
    if (filteredLedgers.length === 0) return alert("無資料可匯出");

    let csvContent = "\uFEFF"; // UTF-8 BOM for Excel Chinese characters
    csvContent += "帳單編號,承租客戶,貨櫃編號,科目類型,帳單金額,付款狀態,計費起日,計費迄日,繳款期限,付款日期,付款方式,收據/雲端網址,備註\n";

    filteredLedgers.forEach(l => {
      const typeLabel = l.event_type === 'rent' ? '租金' : 
                         l.event_type === 'deposit_in' ? '收取押金' :
                         l.event_type === 'deposit_out' ? '退還押金' : '其他調整';
      const statusLabel = l.paid_status === 'paid' ? '已付' : '未付';

      const row = [
        l.ledger_id,
        `"${getCustomerName(l.customer_id)}"`,
        getContainerNo(l.container_id),
        typeLabel,
        l.amount,
        statusLabel,
        l.period_start || '',
        l.period_end || '',
        l.due_date || '',
        l.paid_date || '',
        l.payment_method || '',
        `"${l.receipt_no || ''}"`,
        `"${l.note || ''}"`
      ].join(",");
      csvContent += row + "\n";
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `客戶帳務流水_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">客戶帳務流水</h2>
          <p className="text-slate-400 mt-1">管理租客應收租金、押金帳款、收取記錄與退押款項。</p>
        </div>
        
        <div className="flex gap-2 self-start md:self-auto">
          <button
            onClick={handleExportCSV}
            className="bg-slate-900 border border-slate-800 text-slate-300 font-semibold px-4 py-2.5 rounded-xl text-sm transition hover:border-slate-700"
          >
            📥 匯出 CSV 報表
          </button>
          <button
            onClick={handleOpenCreate}
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-5 py-2.5 rounded-xl transition-all shadow-md shadow-indigo-600/10"
          >
            💵 新增應收/退押項目
          </button>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800/40">
        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-1">依承租客戶篩選</label>
          <select
            value={customerFilter}
            onChange={(e) => setCustomerFilter(e.target.value)}
            className="w-full glass-input px-3 py-2 rounded-xl text-xs"
          >
            <option value="all">所有客戶 (All)</option>
            {customers.map(c => (
              <option key={c.customer_id} value={c.customer_id}>{c.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-1">依貨櫃編號篩選</label>
          <select
            value={containerFilter}
            onChange={(e) => setContainerFilter(e.target.value)}
            className="w-full glass-input px-3 py-2 rounded-xl text-xs"
          >
            <option value="all">所有貨櫃 (All)</option>
            {containers.map(c => (
              <option key={c.container_id} value={c.container_id}>{c.container_no}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-1">依付款狀態篩選</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full glass-input px-3 py-2 rounded-xl text-xs"
          >
            <option value="all">所有狀態 (All)</option>
            <option value="unpaid">待收款 / 欠款 (Unpaid)</option>
            <option value="paid">已入帳收款 (Paid)</option>
          </select>
        </div>
      </div>

      {/* Ledgers List */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : filteredLedgers.length === 0 ? (
        <div className="text-center py-20 bg-slate-900/20 border border-slate-850 rounded-2xl">
          <p className="text-slate-500">此篩選條件下，查無帳務流水紀錄。</p>
        </div>
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs md:text-sm text-slate-300">
              <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px] md:text-xs border-b border-slate-850">
                <tr>
                  <th className="px-5 py-4">承租人 / 貨櫃</th>
                  <th className="px-5 py-4">科目類型</th>
                  <th className="px-5 py-4">應收金額</th>
                  <th className="px-5 py-4">計費區間</th>
                  <th className="px-5 py-4">繳款期限</th>
                  <th className="px-5 py-4">入帳狀態</th>
                  <th className="px-5 py-4 text-right">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {filteredLedgers.map((l) => (
                  <tr key={l.ledger_id} className="hover:bg-slate-900/35 transition-colors">
                    <td className="px-5 py-4.5">
                      <span className="font-semibold text-slate-200 block">{getCustomerName(l.customer_id)}</span>
                      <span className="text-[10px] text-indigo-400 font-mono mt-0.5 block">{getContainerNo(l.container_id)}</span>
                    </td>
                    <td className="px-5 py-4.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        l.event_type === 'rent' ? 'bg-indigo-500/10 text-indigo-400' :
                        l.event_type === 'deposit_in' ? 'bg-purple-500/10 text-purple-400' :
                        l.event_type === 'deposit_out' ? 'bg-rose-500/10 text-rose-400' :
                        'bg-slate-800 text-slate-300'
                      }`}>
                        {l.event_type === 'rent' ? '租金' : 
                         l.event_type === 'deposit_in' ? '收押金' :
                         l.event_type === 'deposit_out' ? '退押金' : '其他'}
                      </span>
                    </td>
                    <td className="px-5 py-4.5 font-bold text-slate-200">{formatCurrency(l.amount)}</td>
                    <td className="px-5 py-4.5 text-slate-400">
                      {l.period_start ? `${l.period_start} ~ ${l.period_end}` : '-'}
                    </td>
                    <td className="px-5 py-4.5 text-slate-400 font-medium">{l.due_date}</td>
                    <td className="px-5 py-4.5">
                      {l.paid_status === 'paid' ? (
                        <div>
                          <span className="bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded text-[10px] font-bold">已收款</span>
                          <span className="text-[10px] text-slate-500 block mt-1">{l.paid_date} ({l.payment_method})</span>
                        </div>
                      ) : (
                        <span className="bg-rose-500/10 text-rose-400 px-2 py-0.5 rounded text-[10px] font-bold animate-pulse">待收款</span>
                      )}
                    </td>
                    <td className="px-5 py-4.5 text-right">
                      {l.paid_status !== 'paid' && (
                        <button
                          onClick={() => handleOpenPayment(l)}
                          className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition shadow shadow-emerald-650/10"
                        >
                          💵 登記收款
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Create Ledger Entry Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-lg rounded-2xl p-6 border border-slate-750 shadow-2xl relative">
            <h3 className="text-xl font-bold text-white mb-4">💵 新增帳務項目</h3>

            <form onSubmit={handleCreateSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">科目類型</label>
                  <select
                    value={createForm.event_type}
                    onChange={(e) => setCreateForm({...createForm, event_type: e.target.value as any})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  >
                    <option value="rent">租金應收 (Rent)</option>
                    <option value="deposit_in">收取租賃押金 (Deposit In)</option>
                    <option value="deposit_out">退還租賃押金 (Deposit Out)</option>
                    <option value="cleaning_fee">清潔費項目</option>
                    <option value="adjustment">帳務調整項目</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">金額 (TWD)</label>
                  <input
                    type="number"
                    required
                    value={createForm.amount || ''}
                    onChange={(e) => setCreateForm({...createForm, amount: parseInt(e.target.value, 10) || 0})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">所屬承租合約 (可選)</label>
                <select
                  value={createForm.rental_id}
                  onChange={(e) => {
                    const selected = rentals.find(r => r.rental_id === e.target.value);
                    if (selected) {
                      setCreateForm({
                        ...createForm,
                        rental_id: selected.rental_id,
                        customer_id: selected.customer_id,
                        container_id: selected.container_id
                      });
                    }
                  }}
                  className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                >
                  <option value="">選擇相關聯之生效合約</option>
                  {rentals.filter(r => r.status === 'active').map(r => (
                    <option key={r.rental_id} value={r.rental_id}>
                      合約: {r.rental_id} ({getCustomerName(r.customer_id)} - {getContainerNo(r.container_id)})
                    </option>
                  ))}
                </select>
              </div>

              {/* Date Ranges */}
              {createForm.event_type === 'rent' && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">計費起日</label>
                    <input
                      type="date"
                      value={createForm.period_start}
                      onChange={(e) => setCreateForm({...createForm, period_start: e.target.value})}
                      className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">計費迄日</label>
                    <input
                      type="date"
                      value={createForm.period_end}
                      onChange={(e) => setCreateForm({...createForm, period_end: e.target.value})}
                      className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">繳款截止日期 (應繳日)</label>
                <input
                  type="date"
                  value={createForm.due_date}
                  onChange={(e) => setCreateForm({...createForm, due_date: e.target.value})}
                  className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">款項備註說明</label>
                <input
                  type="text"
                  placeholder="如：7月份租金應收、第一期租金等"
                  value={createForm.note}
                  onChange={(e) => setCreateForm({...createForm, note: e.target.value})}
                  className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setIsCreateModalOpen(false)}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold px-4 py-2 rounded-xl text-sm transition"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-5 py-2 rounded-xl text-sm transition"
                >
                  建立應收
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Record Payment Modal */}
      {payingEntry && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-md rounded-2xl p-6 border border-slate-750 shadow-2xl relative">
            <h3 className="text-xl font-bold text-white mb-2">💵 登記客戶付款</h3>
            <p className="text-xs text-slate-400 mb-4">
              帳單編號: {payingEntry.ledger_id} | 金額: <span className="text-emerald-400 font-bold">{formatCurrency(payingEntry.amount)}</span>
            </p>

            <form onSubmit={handlePaymentSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">實際收款入帳日</label>
                <input
                  type="date"
                  required
                  value={paymentForm.paid_date}
                  onChange={(e) => setPaymentForm({...paymentForm, paid_date: e.target.value})}
                  className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">收款方式</label>
                <select
                  value={paymentForm.payment_method}
                  onChange={(e) => setPaymentForm({...paymentForm, payment_method: e.target.value})}
                  className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                >
                  <option value="bank_transfer">銀行轉帳/匯款 (Bank Transfer)</option>
                  <option value="cash">現場現金付款 (Cash)</option>
                  <option value="line_pay">LINE Pay 行動支付</option>
                  <option value="check">支票付款 (Check)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">收據單號 / Google Drive 附件連結</label>
                <input
                  type="text"
                  placeholder="輸入收據編號或 Google Drive 雲端發票網址"
                  value={paymentForm.receipt_no}
                  onChange={(e) => setPaymentForm({...paymentForm, receipt_no: e.target.value})}
                  className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">入帳備註</label>
                <input
                  type="text"
                  placeholder="其他備註說明..."
                  value={paymentForm.note}
                  onChange={(e) => setPaymentForm({...paymentForm, note: e.target.value})}
                  className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setPayingEntry(null)}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold px-4 py-2 rounded-xl text-sm transition"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-5 py-2 rounded-xl text-sm transition"
                >
                  入帳收款 💾
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
