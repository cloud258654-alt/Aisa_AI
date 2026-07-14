import { useState, useEffect } from 'react';
import { listCustomers, createCustomer, updateCustomer } from '../services/api/customersApi';
import { listRentals } from '../services/api/rentalsApi';
import { listCustomerLedgers } from '../services/api/customerLedgersApi';
import { Customer } from '../types/customer';
import { RentalRecord } from '../types/rentalRecord';
import { CustomerLedger } from '../types/customerLedger';
import { format } from 'date-fns';
import { useAuth } from '../hooks/useAuth';
import { canDeleteCustomers, canEditCustomers } from '../utils/permissions';

export default function CustomersPage() {
  const { profile } = useAuth();
  const mayEdit = canEditCustomers(profile?.role);
  const mayDelete = canDeleteCustomers(profile?.role);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [rentals, setRentals] = useState<RentalRecord[]>([]);
  const [ledgers, setLedgers] = useState<CustomerLedger[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Search & Filter state
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // Form Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<'create' | 'edit'>('create');
  const [editingId, setEditingId] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    name: '',
    customer_type: 'personal' as 'personal' | 'business',
    phone: '',
    line_id: '',
    email: '',
    tax_id: '',
    billing_address: '',
    status: 'active' as 'active' | 'inactive' | 'blacklisted',
    note: ''
  });

  // Details Modal state
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [selectedCustSummary, setSelectedCustSummary] = useState<{
    rentals: RentalRecord[];
    unpaidLedgers: CustomerLedger[];
    totalUnpaid: number;
    depositBalance: number;
  } | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [custList, rentalList, ledgerList] = await Promise.all([
        listCustomers(),
        listRentals(),
        listCustomerLedgers()
      ]);
      setCustomers(custList);
      setRentals(rentalList);
      setLedgers(ledgerList);
    } catch {
      console.error("Failed to load customer data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenCreate = () => {
    if (!mayEdit) return alert('你目前的角色無權執行此操作');
    setModalMode('create');
    setEditingId(null);
    setFormData({
      name: '',
      customer_type: 'personal',
      phone: '',
      line_id: '',
      email: '',
      tax_id: '',
      billing_address: '',
      status: 'active',
      note: ''
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (customer: Customer) => {
    if (!mayEdit) return alert('你目前的角色無權執行此操作');
    setModalMode('edit');
    setEditingId(customer.customer_id);
    setFormData({
      name: customer.name,
      customer_type: customer.customer_type,
      phone: customer.phone,
      line_id: customer.line_id,
      email: customer.email,
      tax_id: customer.tax_id || '',
      billing_address: customer.billing_address,
      status: customer.status,
      note: customer.note
    });
    setIsModalOpen(true);
  };

  const handleOpenDetails = (customer: Customer) => {
    const custRentals = rentals.filter(r => r.customer_id === customer.customer_id && r.status === 'active');
    const custLedgers = ledgers.filter(l => l.customer_id === customer.customer_id);
    
    // Unpaid bills
    const unpaidList = custLedgers.filter(l => l.paid_status === 'unpaid' || l.paid_status === 'partial');
    const totalUnpaid = unpaidList.reduce((acc, curr) => acc + (Number(curr.amount) || 0), 0);

    // Deposit balance
    let deposit = 0;
    custLedgers.forEach(l => {
      if (l.paid_status === 'paid') {
        if (l.event_type === 'deposit_in') deposit += (Number(l.amount) || 0);
        if (l.event_type === 'deposit_out') deposit -= (Number(l.amount) || 0);
      }
    });

    setSelectedCustomer(customer);
    setSelectedCustSummary({
      rentals: custRentals,
      unpaidLedgers: unpaidList,
      totalUnpaid,
      depositBalance: deposit
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!mayEdit) return alert('你目前的角色無權執行此操作');
    if (!formData.name.trim()) return alert("請輸入客戶名稱");

    try {
      if (modalMode === 'create') {
        await createCustomer(formData);
      } else if (editingId) {
        await updateCustomer(editingId, formData);
      }
      setIsModalOpen(false);
      await loadData();
    } catch {
      alert("儲存客戶資料失敗，已儲存至離線佇列，待網路回復後同步");
      setIsModalOpen(false);
      await loadData();
    }
  };

  const handleToggleStatus = async (customer: Customer) => {
    if (!mayDelete) return alert('你目前的角色無權執行此操作');
    const nextStatus = customer.status === 'active' ? 'inactive' : 'active';
    try {
      await updateCustomer(customer.customer_id, { status: nextStatus });
      await loadData();
    } catch {
      alert("更新狀態失敗，已加入離線佇列");
      await loadData();
    }
  };

  // Filter list
  const filteredCustomers = customers.filter(c => {
    const matchesSearch = c.name.toLowerCase().includes(search.toLowerCase()) || 
                          c.phone.includes(search) || 
                          (c.email && c.email.toLowerCase().includes(search.toLowerCase()));
    
    const matchesStatus = statusFilter === 'all' || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleExportCSV = () => {
    if (filteredCustomers.length === 0) return alert("無資料可匯出");

    let csvContent = "\uFEFF"; // UTF-8 BOM for Excel Chinese characters
    csvContent += "客戶編號,客戶名稱,客戶類型,電話,LINE ID,Email,統一編號,帳單地址,狀態,備註,建立時間\n";

    filteredCustomers.forEach(c => {
      const typeLabel = c.customer_type === 'business' ? '企業客戶' : '個人客戶';
      const statusLabel = c.status === 'active' ? '使用中' : c.status === 'inactive' ? '已停用' : '黑名單';

      const row = [
        c.customer_id,
        `"${c.name}"`,
        typeLabel,
        c.phone,
        c.line_id || '',
        c.email || '',
        c.tax_id || '',
        `"${c.billing_address || ''}"`,
        statusLabel,
        `"${c.note || ''}"`,
        c.created_at
      ].join(",");
      csvContent += row + "\n";
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `客戶清單_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD', maximumFractionDigits: 0 }).format(val);
  };

  return (
    <div className="space-y-6">
      
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">客戶管理</h2>
          <p className="text-slate-400 mt-1">管理個人及企業租客基本資料與帳務總覽。</p>
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
            disabled={!mayEdit}
            title={mayEdit ? undefined : '你目前的角色無權執行此操作'}
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-5 py-2.5 rounded-xl transition-all shadow-md shadow-indigo-600/10"
          >
            ➕ 新增客戶
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col md:flex-row gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800/40">
        <div className="flex-1">
          <input
            type="text"
            placeholder="搜尋姓名、電話、Email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full glass-input px-4 py-2 rounded-xl text-sm"
          />
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setStatusFilter('all')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${statusFilter === 'all' ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30' : 'bg-slate-900 border border-slate-800 text-slate-400'}`}
          >
            全部客戶
          </button>
          <button
            onClick={() => setStatusFilter('active')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${statusFilter === 'active' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-slate-900 border border-slate-800 text-slate-400'}`}
          >
            使用中
          </button>
          <button
            onClick={() => setStatusFilter('inactive')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${statusFilter === 'inactive' ? 'bg-slate-800 text-slate-400 border border-slate-700/60' : 'bg-slate-900 border border-slate-800 text-slate-400'}`}
          >
            已停用
          </button>
        </div>
      </div>

      {/* Customers List View */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : filteredCustomers.length === 0 ? (
        <div className="text-center py-20 bg-slate-900/20 border border-slate-850 rounded-2xl">
          <p className="text-slate-500">找不到符合條件的客戶。</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCustomers.map((cust) => {
            const activeContCount = rentals.filter(r => r.customer_id === cust.customer_id && r.status === 'active').length;
            
            return (
              <div key={cust.customer_id} className="glass-card rounded-2xl p-5 flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-start">
                    <div>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${cust.customer_type === 'business' ? 'bg-purple-500/10 text-purple-400' : 'bg-indigo-500/10 text-indigo-400'}`}>
                        {cust.customer_type === 'business' ? '企業客戶' : '個人客戶'}
                      </span>
                      <h4 className="text-lg font-bold text-white mt-1.5">{cust.name}</h4>
                      <p className="text-xs text-slate-500 mt-0.5">{cust.customer_id}</p>
                    </div>
                    
                    <span className={`text-xs font-semibold px-2 py-1 rounded-lg ${
                      cust.status === 'active' ? 'bg-emerald-500/10 text-emerald-400' : 
                      cust.status === 'inactive' ? 'bg-slate-800 text-slate-400' : 
                      'bg-rose-500/10 text-rose-400'
                    }`}>
                      {cust.status === 'active' ? '使用中' : cust.status === 'inactive' ? '已停用' : '黑名單'}
                    </span>
                  </div>

                  <div className="mt-4 space-y-2 text-sm text-slate-300">
                    <div className="flex items-center gap-2">
                      <span>📞</span>
                      <span>{cust.phone}</span>
                    </div>
                    {cust.line_id && (
                      <div className="flex items-center gap-2">
                        <span className="text-green-500">💬</span>
                        <span className="text-xs text-slate-400">LINE: {cust.line_id}</span>
                      </div>
                    )}
                    {cust.tax_id && (
                      <div className="flex items-center gap-2">
                        <span>🏢</span>
                        <span className="text-xs text-slate-400">統編: {cust.tax_id}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between">
                  <div className="text-xs text-slate-400">
                    目前承租: <span className="text-indigo-400 font-bold">{activeContCount} 櫃</span>
                  </div>
                  
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleOpenDetails(cust)}
                      className="text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg transition"
                    >
                      帳務總覽
                    </button>
                    <button
                      onClick={() => handleOpenEdit(cust)}
                      disabled={!mayEdit}
                      title={mayEdit ? undefined : '你目前的角色無權執行此操作'}
                      className="text-xs font-semibold bg-indigo-950/40 text-indigo-400 hover:bg-indigo-900/40 border border-indigo-900/50 px-3 py-1.5 rounded-lg transition"
                    >
                      編輯
                    </button>
                    <button
                      onClick={() => handleToggleStatus(cust)}
                      disabled={!mayDelete}
                      title={mayDelete ? undefined : '你目前的角色無權執行此操作'}
                      className={`text-xs font-semibold px-2 py-1.5 rounded-lg transition ${
                        cust.status === 'active' ? 'bg-rose-950/20 text-rose-400 border border-rose-950/40 hover:bg-rose-900/20' : 'bg-emerald-950/20 text-emerald-400 border border-emerald-950/40 hover:bg-emerald-900/20'
                      }`}
                    >
                      {cust.status === 'active' ? '停用' : '啟用'}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Add / Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-lg rounded-2xl p-6 border border-slate-750 shadow-2xl relative">
            <h3 className="text-xl font-bold text-white mb-4">
              {modalMode === 'create' ? '➕ 新增客戶資料' : '✏️ 編輯客戶資料'}
            </h3>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">客戶類型</label>
                  <select
                    value={formData.customer_type}
                    onChange={(e) => setFormData({...formData, customer_type: e.target.value as 'personal' | 'business'})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  >
                    <option value="personal">個人客戶</option>
                    <option value="business">企業客戶</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">狀態</label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({...formData, status: e.target.value as Customer['status']})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  >
                    <option value="active">使用中</option>
                    <option value="inactive">已停用</option>
                    <option value="blacklisted">黑名單</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">客戶名稱 / 公司行號</label>
                <input
                  type="text"
                  required
                  placeholder="例如：張小明 或 飛騰物流股份有限公司"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">聯絡電話</label>
                  <input
                    type="text"
                    required
                    placeholder="手機或市話"
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">LINE ID (選填)</label>
                  <input
                    type="text"
                    placeholder="LINE 帳號"
                    value={formData.line_id}
                    onChange={(e) => setFormData({...formData, line_id: e.target.value})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">統一編號 (企業選填)</label>
                  <input
                    type="text"
                    placeholder="8位數統編"
                    value={formData.tax_id}
                    onChange={(e) => setFormData({...formData, tax_id: e.target.value})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">電子郵件 (選填)</label>
                  <input
                    type="email"
                    placeholder="example@mail.com"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">帳單寄送地址</label>
                <input
                  type="text"
                  placeholder="詳細郵寄地址"
                  value={formData.billing_address}
                  onChange={(e) => setFormData({...formData, billing_address: e.target.value})}
                  className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">備註說明</label>
                <textarea
                  placeholder="其他聯絡方式或特別要求..."
                  value={formData.note}
                  onChange={(e) => setFormData({...formData, note: e.target.value})}
                  rows={2}
                  className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold px-4 py-2 rounded-xl text-sm transition"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-5 py-2 rounded-xl text-sm transition shadow-lg shadow-indigo-600/10"
                >
                  儲存
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Details & Ledger Summary Modal */}
      {selectedCustomer && selectedCustSummary && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-2xl rounded-2xl p-6 border border-slate-750 shadow-2xl relative max-h-[90vh] overflow-y-auto">
            
            <div className="flex justify-between items-start border-b border-slate-850 pb-4 mb-4">
              <div>
                <h3 className="text-xl font-bold text-white">{selectedCustomer.name} - 帳務總覽</h3>
                <p className="text-xs text-slate-400 mt-1">系統編號: {selectedCustomer.customer_id}</p>
              </div>
              <button 
                onClick={() => setSelectedCustomer(null)}
                className="text-slate-400 hover:text-slate-200 text-xl font-bold p-1"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div className="p-4 rounded-xl bg-rose-950/15 border border-rose-900/30 flex items-center justify-between">
                <div>
                  <p className="text-xs text-rose-300 font-medium">待收租金欠款</p>
                  <p className="text-xl font-bold text-rose-400 mt-1">{formatCurrency(selectedCustSummary.totalUnpaid)}</p>
                </div>
                <span className="text-xl">💰</span>
              </div>
              <div className="p-4 rounded-xl bg-indigo-950/15 border border-indigo-900/30 flex items-center justify-between">
                <div>
                  <p className="text-xs text-indigo-300 font-medium">保管中押金餘額</p>
                  <p className="text-xl font-bold text-indigo-400 mt-1">{formatCurrency(selectedCustSummary.depositBalance)}</p>
                </div>
                <span className="text-xl">🔐</span>
              </div>
            </div>

            {/* Active Rentals */}
            <div className="space-y-4">
              <h4 className="font-bold text-sm text-slate-200">承租中的合約</h4>
              {selectedCustSummary.rentals.length === 0 ? (
                <p className="text-slate-500 text-xs py-4 border border-dashed border-slate-800 rounded-xl text-center">目前無生效中租約。</p>
              ) : (
                <div className="space-y-3">
                  {selectedCustSummary.rentals.map(r => (
                    <div key={r.rental_id} className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs flex justify-between items-center">
                      <div>
                        <p className="font-bold text-indigo-400">合約: {r.rental_id}</p>
                        <p className="text-slate-400 mt-1">起訖日期: {r.start_date} ~ {r.end_date || '未定'}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-slate-200 font-bold">月租: {formatCurrency(r.monthly_rent)}</p>
                        <p className="text-slate-500 mt-0.5">押金: {formatCurrency(r.deposit_amount)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Unpaid items details */}
            <div className="space-y-4 mt-6">
              <h4 className="font-bold text-sm text-slate-200">待付款明細 ({selectedCustSummary.unpaidLedgers.length} 筆)</h4>
              {selectedCustSummary.unpaidLedgers.length === 0 ? (
                <p className="text-slate-500 text-xs py-4 border border-dashed border-slate-800 rounded-xl text-center">無待繳帳單，帳務狀態良好！</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-900 text-slate-400 uppercase text-[10px]">
                      <tr>
                        <th className="px-3 py-2">項目</th>
                        <th className="px-3 py-2">金額</th>
                        <th className="px-3 py-2">計費區間</th>
                        <th className="px-3 py-2 text-right">應付期限</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 text-slate-300">
                      {selectedCustSummary.unpaidLedgers.map(l => (
                        <tr key={l.ledger_id}>
                          <td className="px-3 py-2.5">
                            <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${l.event_type === 'rent' ? 'bg-indigo-500/10 text-indigo-400' : 'bg-amber-500/10 text-amber-400'}`}>
                              {l.event_type === 'rent' ? '租金' : '其他'}
                            </span>
                          </td>
                          <td className="px-3 py-2.5 font-bold">{formatCurrency(l.amount)}</td>
                          <td className="px-3 py-2.5 text-slate-400">{l.period_start} ~ {l.period_end}</td>
                          <td className="px-3 py-2.5 text-right text-rose-400 font-medium">{l.due_date}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            <div className="flex justify-end pt-6 mt-6 border-t border-slate-850">
              <button
                onClick={() => setSelectedCustomer(null)}
                className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-5 py-2 rounded-xl text-sm transition"
              >
                關閉
              </button>
            </div>
            
          </div>
        </div>
      )}

    </div>
  );
}
