import { useState, useEffect } from 'react';
import { listRentals, createRental, updateRental, terminateRental } from '../services/api/rentalsApi';
import { listCustomers } from '../services/api/customersApi';
import { listContainers } from '../services/api/containersApi';
import { RentalRecord } from '../types/rentalRecord';
import { Customer } from '../types/customer';
import { Container } from '../types/container';
import { format } from 'date-fns';

export default function RentalsPage() {
  const [rentals, setRentals] = useState<RentalRecord[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [containers, setContainers] = useState<Container[]>([]);
  const [loading, setLoading] = useState(true);

  // Search & Filter
  const [statusFilter, setStatusFilter] = useState<string>('active');

  // Create Wizard State
  const [isWizardOpen, setIsWizardOpen] = useState(false);
  const [wizardStep, setWizardStep] = useState(1); // 1: Customer, 2: Container, 3: Terms

  // Form State
  const [selectedCustomerId, setSelectedCustomerId] = useState('');
  const [selectedContainerId, setSelectedContainerId] = useState('');
  const [wizardData, setWizardData] = useState({
    start_date: format(new Date(), 'yyyy-MM-dd'),
    end_date: '',
    billing_cycle: 'monthly' as 'monthly' | 'quarterly' | 'yearly',
    monthly_rent: 5000,
    deposit_amount: 10000,
    payment_due_day: 5,
    create_first_bill: true,
    note: ''
  });

  // Termination Modal State
  const [terminatingRental, setTerminatingRental] = useState<RentalRecord | null>(null);
  const [terminationForm, setTerminationForm] = useState({
    ended_date: format(new Date(), 'yyyy-MM-dd'),
    note: ''
  });

  // Edit Expiration Modal State
  const [editingRental, setEditingRental] = useState<RentalRecord | null>(null);
  const [editForm, setEditForm] = useState({
    end_date: '',
    monthly_rent: 0,
    note: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [rList, cList, contList] = await Promise.all([
        listRentals(),
        listCustomers(),
        listContainers()
      ]);
      setRentals(rList);
      setCustomers(cList);
      setContainers(contList);
    } catch (err) {
      console.error("Failed to load rental data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenWizard = () => {
    setWizardStep(1);
    setSelectedCustomerId('');
    setSelectedContainerId('');
    setWizardData({
      start_date: format(new Date(), 'yyyy-MM-dd'),
      end_date: '',
      billing_cycle: 'monthly',
      monthly_rent: 5000,
      deposit_amount: 10000,
      payment_due_day: 5,
      create_first_bill: true,
      note: ''
    });
    setIsWizardOpen(true);
  };

  const handleNextStep = () => {
    if (wizardStep === 1 && !selectedCustomerId) {
      return alert("請選擇承租客戶");
    }
    if (wizardStep === 2 && !selectedContainerId) {
      return alert("請選擇承租空櫃");
    }
    setWizardStep(prev => prev + 1);
  };

  const handlePrevStep = () => {
    setWizardStep(prev => prev - 1);
  };

  const handleCreateContract = async () => {
    try {
      await createRental({
        customer_id: selectedCustomerId,
        container_id: selectedContainerId,
        start_date: wizardData.start_date,
        end_date: wizardData.end_date,
        billing_cycle: wizardData.billing_cycle,
        monthly_rent: wizardData.monthly_rent,
        deposit_amount: wizardData.deposit_amount,
        payment_due_day: wizardData.payment_due_day,
        status: 'active',
        ended_date: '',
        free_period_start: '',
        free_period_end: '',
        note: wizardData.note
      }, wizardData.create_first_bill);

      setIsWizardOpen(false);
      await loadData();
    } catch (err) {
      alert("簽約成功！部分資料已排入離線佇列等待上傳。");
      setIsWizardOpen(false);
      await loadData();
    }
  };

  const handleOpenTerminate = (rental: RentalRecord) => {
    setTerminatingRental(rental);
    setTerminationForm({
      ended_date: format(new Date(), 'yyyy-MM-dd'),
      note: ''
    });
  };

  const handleConfirmTerminate = async () => {
    if (!terminatingRental) return;
    try {
      await terminateRental(terminatingRental.rental_id, terminationForm.ended_date, terminationForm.note);
      setTerminatingRental(null);
      await loadData();
    } catch (err) {
      alert("退租操作失敗，已加入離線佇列");
      setTerminatingRental(null);
      await loadData();
    }
  };

  const handleOpenEdit = (rental: RentalRecord) => {
    setEditingRental(rental);
    setEditForm({
      end_date: rental.end_date || '',
      monthly_rent: rental.monthly_rent,
      note: rental.note || ''
    });
  };

  const handleConfirmEdit = async () => {
    if (!editingRental) return;
    try {
      await updateRental(editingRental.rental_id, {
        end_date: editForm.end_date,
        monthly_rent: editForm.monthly_rent,
        note: editForm.note
      });
      setEditingRental(null);
      await loadData();
    } catch (err) {
      alert("更新合約失敗，已加入離線佇列");
      setEditingRental(null);
      await loadData();
    }
  };

  const getCustomerName = (id: string) => {
    const c = customers.find(item => item.customer_id === id);
    return c ? c.name : '未知客戶';
  };

  const getContainerNo = (id: string) => {
    const c = containers.find(item => item.container_id === id);
    return c ? c.container_no : '未知貨櫃';
  };

  const handleExportCSV = () => {
    if (filteredRentals.length === 0) return alert("無資料可匯出");

    let csvContent = "\uFEFF"; // UTF-8 BOM for Excel Chinese characters
    csvContent += "租約編號,承租客戶,貨櫃編號,計費週期,月租金,押金金額,起租日期,到期日期,退租日期,狀態,備註,建立時間\n";

    filteredRentals.forEach(r => {
      const statusLabel = r.status === 'active' ? '租賃中' : 
                         r.status === 'ended' ? '已退租' :
                         r.status === 'draft' ? '草稿' : '已取消';

      const row = [
        r.rental_id,
        `"${getCustomerName(r.customer_id)}"`,
        getContainerNo(r.container_id),
        r.billing_cycle,
        r.monthly_rent,
        r.deposit_amount,
        r.start_date,
        r.end_date || '',
        r.ended_date || '',
        statusLabel,
        `"${r.note || ''}"`,
        r.created_at
      ].join(",");
      csvContent += row + "\n";
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `租賃合約清單_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD', maximumFractionDigits: 0 }).format(val);
  };

  // Filter rentals
  const filteredRentals = rentals.filter(r => {
    const matchesStatus = statusFilter === 'all' || r.status === statusFilter;
    return matchesStatus;
  });

  // Filtered available containers for contracting
  const availableContainers = containers.filter(c => c.status === 'available');

  return (
    <div className="space-y-6">
      
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">租約合約管理</h2>
          <p className="text-slate-400 mt-1">建立新約、登記退租、到期日追蹤與續租費率調整。</p>
        </div>
        <div className="flex gap-2 self-start md:self-auto">
          <button
            onClick={handleExportCSV}
            className="bg-slate-900 border border-slate-800 text-slate-300 font-semibold px-4 py-2.5 rounded-xl text-sm transition hover:border-slate-700"
          >
            📥 匯出 CSV
          </button>
          <button
            onClick={handleOpenWizard}
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-5 py-2.5 rounded-xl transition-all shadow-md shadow-indigo-600/10"
          >
            📜 建立新租約
          </button>
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2 border-b border-slate-800 pb-3">
        <button
          onClick={() => setStatusFilter('active')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${statusFilter === 'active' ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30' : 'bg-transparent text-slate-400 hover:text-slate-200'}`}
        >
          租賃中 (Active)
        </button>
        <button
          onClick={() => setStatusFilter('ended')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${statusFilter === 'ended' ? 'bg-slate-800 text-slate-400 border border-slate-700/60' : 'bg-transparent text-slate-400 hover:text-slate-200'}`}
        >
          已退租 (Ended)
        </button>
        <button
          onClick={() => setStatusFilter('all')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${statusFilter === 'all' ? 'bg-indigo-500/10 text-slate-300' : 'bg-transparent text-slate-400 hover:text-slate-200'}`}
        >
          全部合約
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : filteredRentals.length === 0 ? (
        <div className="text-center py-20 bg-slate-900/20 border border-slate-850 rounded-2xl">
          <p className="text-slate-500">此狀態下目前無任何合約紀錄。</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredRentals.map((r) => (
            <div key={r.rental_id} className="glass-card rounded-2xl p-5 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-[10px] text-slate-500 font-mono font-bold block">{r.rental_id}</span>
                    <h4 className="text-lg font-bold text-white mt-1">
                      承租: {getContainerNo(r.container_id)}
                    </h4>
                    <p className="text-xs text-slate-400 mt-1">客戶: {getCustomerName(r.customer_id)}</p>
                  </div>
                  
                  <span className={`text-xs font-semibold px-2 py-1 rounded-lg ${
                    r.status === 'active' ? 'bg-indigo-500/10 text-indigo-400' : 
                    r.status === 'ended' ? 'bg-slate-800 text-slate-400' : 'bg-rose-500/10 text-rose-400'
                  }`}>
                    {r.status === 'active' ? '租賃中' : r.status === 'ended' ? '已退租' : '已取消'}
                  </span>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-4 text-xs bg-slate-950/40 p-3 rounded-xl border border-slate-900/50">
                  <div>
                    <span className="text-slate-500 block">租約起日</span>
                    <span className="font-semibold text-slate-200">{r.start_date}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">預計迄日</span>
                    <span className="font-semibold text-slate-200">{r.end_date || '未定 (長期合約)'}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">月租金</span>
                    <span className="font-semibold text-indigo-400">{formatCurrency(r.monthly_rent)}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">押金金額</span>
                    <span className="font-semibold text-purple-400">{formatCurrency(r.deposit_amount)}</span>
                  </div>
                </div>

                {r.ended_date && (
                  <p className="text-xs text-rose-400 mt-3 font-semibold">
                    🚫 已於 {r.ended_date} 退櫃結案
                  </p>
                )}

                {r.note && (
                  <p className="text-xs text-slate-400 mt-3 bg-slate-900/40 p-2.5 rounded border border-slate-900">
                    備註: {r.note}
                  </p>
                )}
              </div>

              {r.status === 'active' && (
                <div className="mt-6 pt-4 border-t border-slate-800/80 flex justify-end gap-2">
                  <button
                    onClick={() => handleOpenEdit(r)}
                    className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3.5 py-2 rounded-lg transition"
                  >
                    續約/調整
                  </button>
                  <button
                    onClick={() => handleOpenTerminate(r)}
                    className="text-xs bg-rose-950/20 text-rose-400 border border-rose-950/40 hover:bg-rose-900/20 px-3.5 py-2 rounded-lg transition"
                  >
                    辦理退租
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Contracting Wizard Modal */}
      {isWizardOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-lg rounded-2xl p-6 border border-slate-750 shadow-2xl relative">
            
            {/* Header / Step Bar */}
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-white">建立合約 - 步驟 {wizardStep} / 3</h3>
              <button onClick={() => setIsWizardOpen(false)} className="text-slate-400 hover:text-slate-200">✕</button>
            </div>

            {/* Wizard Step 1: Select Customer */}
            {wizardStep === 1 && (
              <div className="space-y-4">
                <label className="block text-sm font-semibold text-slate-300">選擇承租客戶</label>
                <div className="max-h-60 overflow-y-auto space-y-2">
                  {customers.filter(c => c.status === 'active').map(c => (
                    <div
                      key={c.customer_id}
                      onClick={() => setSelectedCustomerId(c.customer_id)}
                      className={`p-3 rounded-xl border cursor-pointer text-sm transition-all ${
                        selectedCustomerId === c.customer_id
                          ? 'bg-indigo-650/20 border-indigo-500 text-white font-medium'
                          : 'bg-slate-900/40 border-slate-800 text-slate-400 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex justify-between">
                        <span>{c.name}</span>
                        <span className="text-xs text-slate-500">{c.phone}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Wizard Step 2: Select Container */}
            {wizardStep === 2 && (
              <div className="space-y-4">
                <label className="block text-sm font-semibold text-slate-300">選擇可用空櫃</label>
                {availableContainers.length === 0 ? (
                  <p className="text-amber-400 text-xs py-4 text-center">園區內目前已無空置貨櫃，請先於「貨櫃管理」新增或變更狀態。</p>
                ) : (
                  <div className="max-h-60 overflow-y-auto space-y-2">
                    {availableContainers.map(c => (
                      <div
                        key={c.container_id}
                        onClick={() => setSelectedContainerId(c.container_id)}
                        className={`p-3 rounded-xl border cursor-pointer text-sm transition-all ${
                          selectedContainerId === c.container_id
                            ? 'bg-indigo-650/20 border-indigo-500 text-white font-medium'
                            : 'bg-slate-900/40 border-slate-800 text-slate-400 hover:border-slate-700'
                        }`}
                      >
                        <div className="flex justify-between">
                          <span className="font-bold text-slate-200">{c.container_no}</span>
                          <span className="text-xs text-slate-400">{c.size_ft}呎 · {c.location_zone}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Wizard Step 3: Contract Terms */}
            {wizardStep === 3 && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">起租日期</label>
                    <input
                      type="date"
                      value={wizardData.start_date}
                      onChange={(e) => setWizardData({...wizardData, start_date: e.target.value})}
                      className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">合約到期日 (選填)</label>
                    <input
                      type="date"
                      value={wizardData.end_date}
                      onChange={(e) => setWizardData({...wizardData, end_date: e.target.value})}
                      className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">每月租金 (TWD)</label>
                    <input
                      type="number"
                      value={wizardData.monthly_rent}
                      onChange={(e) => setWizardData({...wizardData, monthly_rent: parseInt(e.target.value, 10) || 0})}
                      className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">合約押金 (TWD)</label>
                    <input
                      type="number"
                      value={wizardData.deposit_amount}
                      onChange={(e) => setWizardData({...wizardData, deposit_amount: parseInt(e.target.value, 10) || 0})}
                      className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">計費週期</label>
                    <select
                      value={wizardData.billing_cycle}
                      onChange={(e) => setWizardData({...wizardData, billing_cycle: e.target.value as any})}
                      className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                    >
                      <option value="monthly">每月繳 (Monthly)</option>
                      <option value="quarterly">每季繳 (Quarterly)</option>
                      <option value="yearly">每年繳 (Yearly)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">每月收款繳款日</label>
                    <input
                      type="number"
                      min={1}
                      max={28}
                      placeholder="5"
                      value={wizardData.payment_due_day}
                      onChange={(e) => setWizardData({...wizardData, payment_due_day: parseInt(e.target.value, 10) || 1})}
                      className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">合約備註說明</label>
                  <input
                    type="text"
                    placeholder="如：優惠條款、其他聯絡人等"
                    value={wizardData.note}
                    onChange={(e) => setWizardData({...wizardData, note: e.target.value})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  />
                </div>

                {/* Auto Invoice Generation Toggle */}
                <div className="p-3.5 rounded-xl bg-indigo-950/20 border border-indigo-900/30 flex items-center justify-between">
                  <div>
                    <h5 className="text-xs font-bold text-slate-200">建立首期帳務流水</h5>
                    <p className="text-[10px] text-slate-400 mt-0.5">系統將自動產生押金應收與第一期租金待付帳單。</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={wizardData.create_first_bill}
                    onChange={(e) => setWizardData({...wizardData, create_first_bill: e.target.checked})}
                    className="w-4 h-4 text-indigo-600 rounded bg-slate-900 border-slate-800"
                  />
                </div>
              </div>
            )}

            {/* Bottom Buttons */}
            <div className="flex justify-between pt-6 mt-6 border-t border-slate-850">
              {wizardStep > 1 ? (
                <button
                  onClick={handlePrevStep}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold px-4 py-2 rounded-xl text-sm transition"
                >
                  上一步
                </button>
              ) : (
                <div></div>
              )}

              <div className="flex gap-2">
                <button
                  onClick={() => setIsWizardOpen(false)}
                  className="bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 font-semibold px-4 py-2 rounded-xl text-sm transition"
                >
                  取消
                </button>

                {wizardStep < 3 ? (
                  <button
                    onClick={handleNextStep}
                    className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-5 py-2 rounded-xl text-sm transition shadow-lg shadow-indigo-600/10"
                  >
                    下一步
                  </button>
                ) : (
                  <button
                    onClick={handleCreateContract}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-5 py-2 rounded-xl text-sm transition shadow-lg shadow-emerald-600/10"
                  >
                    確認簽約 💾
                  </button>
                )}
              </div>
            </div>

          </div>
        </div>
      )}

      {/* Termination Modal */}
      {terminatingRental && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-md rounded-2xl p-6 border border-slate-750 shadow-2xl relative">
            <h3 className="text-xl font-bold text-white mb-2">辦理退租手續</h3>
            <p className="text-xs text-slate-400 mb-4">
              合約: {terminatingRental.rental_id} ({getContainerNo(terminatingRental.container_id)})
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">實際退櫃日期</label>
                <input
                  type="date"
                  value={terminationForm.ended_date}
                  onChange={(e) => setTerminationForm({...terminationForm, ended_date: e.target.value})}
                  className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">退租結案備註說明</label>
                <textarea
                  placeholder="如：清空無損、已退還扣除水電後之押金等資訊..."
                  value={terminationForm.note}
                  onChange={(e) => setTerminationForm({...terminationForm, note: e.target.value})}
                  rows={3}
                  className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                />
              </div>

              <div className="p-3 bg-amber-500/10 border border-amber-500/20 text-[10px] text-amber-300 rounded-xl leading-relaxed">
                ⚠️ 注意：辦理退租結案後，該貨櫃狀態將會自動變更回「空櫃 (available)」，且此合約將不可再編輯或修改。
              </div>

              <div className="flex justify-end gap-3 pt-3">
                <button
                  onClick={() => setTerminatingRental(null)}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold px-4 py-2 rounded-xl text-sm transition"
                >
                  取消
                </button>
                <button
                  onClick={handleConfirmTerminate}
                  className="bg-rose-600 hover:bg-rose-500 text-white font-semibold px-5 py-2 rounded-xl text-sm transition shadow-lg shadow-rose-600/10"
                >
                  確認結案 🚫
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Expiration/Terms Modal */}
      {editingRental && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-md rounded-2xl p-6 border border-slate-750 shadow-2xl relative">
            <h3 className="text-xl font-bold text-white mb-2">調整合約條件 / 續約</h3>
            <p className="text-xs text-slate-400 mb-4">
              合約: {editingRental.rental_id} ({getContainerNo(editingRental.container_id)})
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">新的合約到期日</label>
                <input
                  type="date"
                  value={editForm.end_date}
                  onChange={(e) => setEditForm({...editForm, end_date: e.target.value})}
                  className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">調整後每月租金 (TWD)</label>
                <input
                  type="number"
                  value={editForm.monthly_rent}
                  onChange={(e) => setEditForm({...editForm, monthly_rent: parseInt(e.target.value, 10) || 0})}
                  className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">異動備註說明</label>
                <textarea
                  placeholder="請輸入調整或續約之依據備註..."
                  value={editForm.note}
                  onChange={(e) => setEditForm({...editForm, note: e.target.value})}
                  rows={2}
                  className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3">
                <button
                  onClick={() => setEditingRental(null)}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold px-4 py-2 rounded-xl text-sm transition"
                >
                  取消
                </button>
                <button
                  onClick={handleConfirmEdit}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-5 py-2 rounded-xl text-sm transition shadow-lg shadow-indigo-600/10"
                >
                  確認修改 💾
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
