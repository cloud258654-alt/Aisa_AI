import { useState, useEffect } from 'react';
import { listManagementLedgers, createManagementLedgerEntry, updateManagementLedgerEntry } from '../services/api/managementLedgersApi';
import { listContainers } from '../services/api/containersApi';
import { ManagementLedger } from '../types/managementLedger';
import { Container } from '../types/container';
import { format } from 'date-fns';

export default function ManagementLedgersPage() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [ledgers, setLedgers] = useState<ManagementLedger[]>([]);
  const [containers, setContainers] = useState<Container[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [containerFilter, setContainerFilter] = useState('all');
  const [expenseFilter, setExpenseFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  // Create Modal State
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    container_id: '', // empty means general site
    expense_type: 'maintenance' as ManagementLedger['expense_type'],
    vendor: '',
    amount: 0,
    paid_status: 'unpaid' as ManagementLedger['paid_status'],
    record_date: format(new Date(), 'yyyy-MM-dd'),
    due_date: format(new Date(), 'yyyy-MM-dd'),
    payment_method: 'bank_transfer',
    receipt_no: '',
    is_capitalized: false,
    issue_desc: ''
  });

  // Record Payment Modal State
  const [payingEntry, setPayingEntry] = useState<ManagementLedger | null>(null);
  const [paymentForm, setPaymentForm] = useState({
    paid_date: format(new Date(), 'yyyy-MM-dd'),
    payment_method: 'bank_transfer',
    receipt_no: ''
  });

  useEffect(() => {
    const online = () => setIsOnline(true);
    const offline = () => setIsOnline(false);
    window.addEventListener('online', online);
    window.addEventListener('offline', offline);

    loadData();

    return () => {
      window.removeEventListener('online', online);
      window.removeEventListener('offline', offline);
    };
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [lList, contList] = await Promise.all([
        listManagementLedgers(),
        listContainers()
      ]);
      setLedgers(lList);
      setContainers(contList);
    } catch (err) {
      console.error("Failed to load management ledgers:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenCreate = () => {
    if (!isOnline) return alert('目前離線，恢復網路後才能儲存');
    setCreateForm({
      container_id: '',
      expense_type: 'maintenance',
      vendor: '',
      amount: 1000,
      paid_status: 'unpaid',
      record_date: format(new Date(), 'yyyy-MM-dd'),
      due_date: format(new Date(), 'yyyy-MM-dd'),
      payment_method: 'bank_transfer',
      receipt_no: '',
      is_capitalized: false,
      issue_desc: ''
    });
    setIsCreateOpen(true);
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isOnline) return alert('目前離線，恢復網路後才能儲存');
    if (createForm.amount <= 0) return alert("金額必須大於 0");

    try {
      await createManagementLedgerEntry({
        ...createForm,
        paid_date: createForm.paid_status === 'paid' ? createForm.record_date : ''
      });
      setIsCreateOpen(false);
      await loadData();
    } catch (err: unknown) {
      alert("支出登記失敗: " + (err instanceof Error ? err.message : '未知錯誤'));
    }
  };

  const handleOpenPayment = (entry: ManagementLedger) => {
    if (!isOnline) return alert('目前離線，恢復網路後才能儲存');
    setPayingEntry(entry);
    setPaymentForm({
      paid_date: format(new Date(), 'yyyy-MM-dd'),
      payment_method: 'bank_transfer',
      receipt_no: entry.receipt_no || ''
    });
  };

  const handlePaymentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isOnline) return alert('目前離線，恢復網路後才能儲存');
    if (!payingEntry) return;

    try {
      await updateManagementLedgerEntry(payingEntry.ledger_id, {
        paid_status: 'paid',
        paid_date: paymentForm.paid_date,
        payment_method: paymentForm.payment_method,
        receipt_no: paymentForm.receipt_no
      });
      setPayingEntry(null);
      await loadData();
    } catch (err: unknown) {
      alert("標記付款失敗: " + (err instanceof Error ? err.message : '未知錯誤'));
    }
  };

  const getContainerNo = (id?: string) => {
    if (!id) return '全場共用/場地費用';
    const c = containers.find(item => item.container_id === id);
    return c ? `貨櫃: ${c.container_no}` : '未知貨櫃';
  };

  const handleExportCSV = () => {
    if (filteredLedgers.length === 0) return alert("無資料可匯出");

    let csvContent = "\uFEFF"; // UTF-8 BOM for Excel Chinese characters
    csvContent += "支出編號,關聯貨櫃,科目種類,支出金額,供應商,登記日期,付款狀態,付款日期,付款方式,憑證網址,資本化否,支出說明\n";

    filteredLedgers.forEach(l => {
      const typeLabel = getExpenseTypeLabel(l.expense_type);
      const capLabel = l.is_capitalized ? '是' : '否';
      const statusLabel = l.paid_status === 'paid' ? '已付清' : '未付';

      const row = [
        l.ledger_id,
        getContainerNo(l.container_id),
        typeLabel,
        l.amount,
        `"${l.vendor || ''}"`,
        l.record_date,
        statusLabel,
        l.paid_date || '',
        l.payment_method || '',
        `"${l.receipt_no || ''}"`,
        capLabel,
        `"${l.issue_desc || ''}"`
      ].join(",");
      csvContent += row + "\n";
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `場地支出清單_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD', maximumFractionDigits: 0 }).format(val);
  };

  const getExpenseTypeLabel = (type: ManagementLedger['expense_type']) => {
    switch (type) {
      case 'maintenance': return '貨櫃修繕';
      case 'land_rent': return '場地地租';
      case 'utilities': return '水電照明';
      case 'security': return '保全監控';
      case 'ads': return '廣告行銷';
      case 'cleaning': return '清潔整理';
      case 'transport': return '搬運運輸';
      case 'renovation': return '裝潢改善';
      default: return '其他支出';
    }
  };

  // Filter ledgers
  const filteredLedgers = ledgers.filter(l => {
    const matchCont = containerFilter === 'all' || 
                       (containerFilter === 'general' && !l.container_id) || 
                       l.container_id === containerFilter;
    const matchExpense = expenseFilter === 'all' || l.expense_type === expenseFilter;
    const matchStatus = statusFilter === 'all' || l.paid_status === statusFilter;
    return matchCont && matchExpense && matchStatus;
  });

  return (
    <div className="space-y-6">
      
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">場地營運支出</h2>
          <p className="text-slate-400 mt-1">登記貨櫃修繕、場地地租、水電費、保全監控等支出流水。</p>
        </div>
        <div className="flex gap-2 self-start md:self-auto">
          <button
            onClick={handleExportCSV}
            className="bg-slate-900 border border-slate-800 text-slate-300 font-semibold px-4 py-2.5 rounded-xl text-sm transition hover:border-slate-700"
          >
            📥 匯出 CSV
          </button>
          <button
            onClick={handleOpenCreate}
            disabled={!isOnline}
            title={isOnline ? undefined : '目前離線，恢復網路後才能儲存'}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold px-5 py-2.5 rounded-xl transition-all shadow-md shadow-indigo-600/10"
          >
            🛠️ 登記支出費用
          </button>
        </div>
      </div>

      {/* Offline Alert */}
      {!isOnline && (
        <div className="p-3 bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs rounded-xl text-center">
          ⚠️ 目前處於離線狀態，已顯示最近一次載入的暫存資料（可能不是最新資料）。請恢復網路連線以進行新增、修改或刪除操作。
        </div>
      )}

      {/* Filters Bar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800/40">
        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-1">依貨櫃/共用費用篩選</label>
          <select
            value={containerFilter}
            onChange={(e) => setContainerFilter(e.target.value)}
            className="w-full glass-input px-3 py-2 rounded-xl text-xs"
          >
            <option value="all">所有項目 (All)</option>
            <option value="general">全場共用/場地費用</option>
            {containers.map(c => (
              <option key={c.container_id} value={c.container_id}>{c.container_no}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-1">依費用科目篩選</label>
          <select
            value={expenseFilter}
            onChange={(e) => setExpenseFilter(e.target.value)}
            className="w-full glass-input px-3 py-2 rounded-xl text-xs"
          >
            <option value="all">所有科目 (All)</option>
            <option value="maintenance">貨櫃修繕 (Maintenance)</option>
            <option value="land_rent">場地地租 (Land Rent)</option>
            <option value="utilities">水電照明 (Utilities)</option>
            <option value="security">保全監控 (Security)</option>
            <option value="ads">廣告行銷 (Ads)</option>
            <option value="cleaning">清潔整理 (Cleaning)</option>
            <option value="transport">搬運運輸 (Transport)</option>
            <option value="renovation">裝潢改善 (Renovation)</option>
            <option value="other">其他費用 (Other)</option>
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
            <option value="unpaid">未付款 / 應付 (Unpaid)</option>
            <option value="paid">已付款 (Paid)</option>
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
          <p className="text-slate-500">查無任何符合條件的營運支出流水。</p>
        </div>
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs md:text-sm text-slate-300">
              <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px] md:text-xs border-b border-slate-850">
                <tr>
                  <th className="px-5 py-4">關聯貨櫃 / 共用</th>
                  <th className="px-5 py-4">費用類型</th>
                  <th className="px-5 py-4">支出金額</th>
                  <th className="px-5 py-4">供應商</th>
                  <th className="px-5 py-4">登記日期</th>
                  <th className="px-5 py-4">付款狀態</th>
                  <th className="px-5 py-4 text-right">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {filteredLedgers.map((l) => (
                  <tr key={l.ledger_id} className="hover:bg-slate-900/35 transition-colors">
                    <td className="px-5 py-4.5">
                      <span className="font-semibold text-slate-200 block">{getContainerNo(l.container_id)}</span>
                      <span className="text-[10px] text-slate-500 font-mono mt-0.5 block">{l.ledger_id}</span>
                    </td>
                    <td className="px-5 py-4.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        l.is_capitalized ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'bg-slate-800 text-slate-300'
                      }`}>
                        {getExpenseTypeLabel(l.expense_type)}
                        {l.is_capitalized && ' (資本化)'}
                      </span>
                      {l.issue_desc && (
                        <p className="text-[11px] text-slate-400 mt-1 max-w-[180px] truncate" title={l.issue_desc}>
                          {l.issue_desc}
                        </p>
                      )}
                    </td>
                    <td className="px-5 py-4.5 font-bold text-slate-200">{formatCurrency(l.amount)}</td>
                    <td className="px-5 py-4.5 text-slate-300">{l.vendor || '-'}</td>
                    <td className="px-5 py-4.5 text-slate-400">{l.record_date}</td>
                    <td className="px-5 py-4.5">
                      {l.paid_status === 'paid' ? (
                        <div>
                          <span className="bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded text-[10px] font-bold">已付</span>
                          <span className="text-[10px] text-slate-500 block mt-1">{l.paid_date} ({l.payment_method})</span>
                        </div>
                      ) : (
                        <span className="bg-amber-500/10 text-amber-400 px-2 py-0.5 rounded text-[10px] font-bold animate-pulse">待付款</span>
                      )}
                    </td>
                    <td className="px-5 py-4.5 text-right">
                      {l.paid_status !== 'paid' && (
                        <button
                          onClick={() => handleOpenPayment(l)}
                          disabled={!isOnline}
                          title={isOnline ? undefined : '目前離線，恢復網路後才能儲存'}
                          className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition shadow"
                        >
                          💵 標記付款
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

      {/* Create Expense Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-lg rounded-2xl p-6 border border-slate-750 shadow-2xl relative">
            <h3 className="text-xl font-bold text-white mb-4">🛠️ 登記營運支出項目</h3>

            <form onSubmit={handleCreateSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">費用類型</label>
                  <select
                    value={createForm.expense_type}
                    onChange={(e) => setCreateForm({...createForm, expense_type: e.target.value as ManagementLedger['expense_type']})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  >
                    <option value="maintenance">貨櫃修繕 (Maintenance)</option>
                    <option value="land_rent">場地地租 (Land Rent)</option>
                    <option value="utilities">水電照明 (Utilities)</option>
                    <option value="security">保全監控 (Security)</option>
                    <option value="ads">廣告行銷 (Ads)</option>
                    <option value="cleaning">清潔整理 (Cleaning)</option>
                    <option value="transport">搬運運輸 (Transport)</option>
                    <option value="renovation">裝潢改善 (Renovation)</option>
                    <option value="other">其他費用支出 (Other)</option>
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

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">所屬特定貨櫃 (選填)</label>
                  <select
                    value={createForm.container_id}
                    onChange={(e) => setCreateForm({...createForm, container_id: e.target.value})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  >
                    <option value="">全場共用 / 場地公攤費用</option>
                    {containers.map(c => (
                      <option key={c.container_id} value={c.container_id}>{c.container_no}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">收款商家/廠商 (選填)</label>
                  <input
                    type="text"
                    placeholder="供應商名稱"
                    value={createForm.vendor}
                    onChange={(e) => setCreateForm({...createForm, vendor: e.target.value})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">登記/紀錄日期</label>
                  <input
                    type="date"
                    required
                    value={createForm.record_date}
                    onChange={(e) => setCreateForm({...createForm, record_date: e.target.value})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">付款截止日 (應付日)</label>
                  <input
                    type="date"
                    required
                    value={createForm.due_date}
                    onChange={(e) => setCreateForm({...createForm, due_date: e.target.value})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">付款狀態</label>
                  <select
                    value={createForm.paid_status}
                    onChange={(e) => setCreateForm({...createForm, paid_status: e.target.value as ManagementLedger['paid_status']})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  >
                    <option value="unpaid">未付 (Unpaid)</option>
                    <option value="paid">已付 (Paid)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">收據單號 / 附件連結</label>
                  <input
                    type="text"
                    placeholder="發票編號或 Drive 連結"
                    value={createForm.receipt_no}
                    onChange={(e) => setCreateForm({...createForm, receipt_no: e.target.value})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">支出事由說明</label>
                <textarea
                  placeholder="如：貨櫃除鏽與防油漆修繕工程、8月份地租項目..."
                  value={createForm.issue_desc}
                  onChange={(e) => setCreateForm({...createForm, issue_desc: e.target.value})}
                  rows={2}
                  className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                />
              </div>

              {/* Capitalized Toggle */}
              <div className="p-3 rounded-xl bg-slate-950/45 border border-slate-900 flex items-center justify-between">
                <div>
                  <h5 className="text-xs font-bold text-slate-200">將此費用資本化 (Capitalized Expense)</h5>
                  <p className="text-[10px] text-slate-500 mt-0.5">若此支出會增加貨櫃價值或使用年限（如重大翻新），請勾選。</p>
                </div>
                <input
                  type="checkbox"
                  checked={createForm.is_capitalized}
                  onChange={(e) => setCreateForm({...createForm, is_capitalized: e.target.checked})}
                  className="w-4 h-4 text-indigo-600 rounded bg-slate-900 border-slate-850"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setIsCreateOpen(false)}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold px-4 py-2 rounded-xl text-sm transition"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-5 py-2 rounded-xl text-sm transition"
                >
                  登記支出
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
            <h3 className="text-xl font-bold text-white mb-2">登記支出付款</h3>
            <p className="text-xs text-slate-400 mb-4">
              支出編號: {payingEntry.ledger_id} | 金額: <span className="text-rose-400 font-bold">{formatCurrency(payingEntry.amount)}</span>
            </p>

            <form onSubmit={handlePaymentSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">實際付款日期</label>
                <input
                  type="date"
                  required
                  value={paymentForm.paid_date}
                  onChange={(e) => setPaymentForm({...paymentForm, paid_date: e.target.value})}
                  className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">付款方式</label>
                <select
                  value={paymentForm.payment_method}
                  onChange={(e) => setPaymentForm({...paymentForm, payment_method: e.target.value})}
                  className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                >
                  <option value="bank_transfer">銀行匯款/轉帳 (Bank Transfer)</option>
                  <option value="cash">現金支付 (Cash)</option>
                  <option value="credit_card">信用卡/融資扣款</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">發票收據單號 / Google Drive 雲端發票連結</label>
                <input
                  type="text"
                  placeholder="輸入發票單號或雲端收據連結"
                  value={paymentForm.receipt_no}
                  onChange={(e) => setPaymentForm({...paymentForm, receipt_no: e.target.value})}
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
                  確認已付款 💾
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
