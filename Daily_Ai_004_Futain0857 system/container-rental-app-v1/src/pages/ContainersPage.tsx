import { useState, useEffect } from 'react';
import { listContainers, createContainer, updateContainer } from '../services/api/containersApi';
import { Container } from '../types/container';
import { format } from 'date-fns';

export default function ContainersPage() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [containers, setContainers] = useState<Container[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Search & Filter
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // Add / Edit Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<'create' | 'edit'>('create');
  const [editingId, setEditingId] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    container_no: '',
    size_ft: 20,
    container_type: 'standard',
    location_zone: 'A區',
    location_label: '',
    total_setup_cost: 0,
    status: 'available' as 'available' | 'rented' | 'maintenance' | 'retired',
    note: ''
  });

  useEffect(() => {
    const online = () => setIsOnline(true);
    const offline = () => setIsOnline(false);
    window.addEventListener('online', online);
    window.addEventListener('offline', offline);

    loadContainers();

    return () => {
      window.removeEventListener('online', online);
      window.removeEventListener('offline', offline);
    };
  }, []);

  const loadContainers = async () => {
    try {
      setLoading(true);
      const data = await listContainers();
      setContainers(data);
    } catch (err) {
      console.error("Failed to load containers:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenCreate = () => {
    if (!isOnline) return alert('目前離線，恢復網路後才能儲存');
    setModalMode('create');
    setEditingId(null);
    setFormData({
      container_no: '',
      size_ft: 20,
      container_type: 'standard',
      location_zone: 'A區',
      location_label: '',
      total_setup_cost: 0,
      status: 'available',
      note: ''
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (container: Container) => {
    if (!isOnline) return alert('目前離線，恢復網路後才能儲存');
    setModalMode('edit');
    setEditingId(container.container_id);
    setFormData({
      container_no: container.container_no,
      size_ft: container.size_ft,
      container_type: container.container_type,
      location_zone: container.location_zone,
      location_label: container.location_label,
      total_setup_cost: container.total_setup_cost,
      status: container.status,
      note: container.note
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isOnline) return alert('目前離線，恢復網路後才能儲存');
    if (!formData.container_no.trim()) return alert("請輸入貨櫃編號");

    try {
      if (modalMode === 'create') {
        await createContainer(formData);
      } else if (editingId) {
        await updateContainer(editingId, formData);
      }
      setIsModalOpen(false);
      await loadContainers();
    } catch (err: unknown) {
      alert("儲存貨櫃失敗: " + (err instanceof Error ? err.message : '未知錯誤'));
    }
  };

  const handleQuickStatusChange = async (id: string, newStatus: Container['status']) => {
    if (!isOnline) return alert('目前離線，恢復網路後才能儲存');
    try {
      await updateContainer(id, { status: newStatus });
      await loadContainers();
    } catch (err: unknown) {
      alert("更新狀態失敗: " + (err instanceof Error ? err.message : '未知錯誤'));
    }
  };

  // Filter & Search
  const filteredContainers = containers.filter(c => {
    const matchesSearch = c.container_no.toLowerCase().includes(search.toLowerCase()) || 
                          c.location_zone.toLowerCase().includes(search.toLowerCase()) || 
                          (c.location_label && c.location_label.toLowerCase().includes(search.toLowerCase()));
    const matchesStatus = statusFilter === 'all' || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: Container['status']) => {
    switch (status) {
      case 'available':
        return <span className="bg-emerald-500/10 text-emerald-400 text-xs font-semibold px-2.5 py-1 rounded-full">空櫃</span>;
      case 'rented':
        return <span className="bg-indigo-500/10 text-indigo-400 text-xs font-semibold px-2.5 py-1 rounded-full">出租中</span>;
      case 'maintenance':
        return <span className="bg-amber-500/10 text-amber-400 text-xs font-semibold px-2.5 py-1 rounded-full">維修中</span>;
      case 'retired':
        return <span className="bg-slate-800 text-slate-400 text-xs font-semibold px-2.5 py-1 rounded-full">停用</span>;
      default:
        return null;
    }
  };

  const handleExportCSV = () => {
    if (filteredContainers.length === 0) return alert("無資料可匯出");

    let csvContent = "\uFEFF"; // UTF-8 BOM for Excel Chinese characters
    csvContent += "貨櫃識別碼,貨櫃編號,尺寸(呎),種類,存放園區,位置標記,建置成本,狀態,備註,建立時間\n";

    filteredContainers.forEach(c => {
      const statusLabel = c.status === 'available' ? '空櫃' : 
                         c.status === 'rented' ? '出租中' :
                         c.status === 'maintenance' ? '維修中' : '已停用';

      const row = [
        c.container_id,
        c.container_no,
        c.size_ft,
        c.container_type,
        c.location_zone,
        c.location_label,
        c.total_setup_cost,
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
    link.setAttribute("download", `貨櫃清單_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`);
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
          <h2 className="text-3xl font-extrabold text-white tracking-tight">貨櫃管理</h2>
          <p className="text-slate-400 mt-1">追蹤貨櫃庫存、狀態、尺寸與所屬園區位置。</p>
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
            📦 新增貨櫃
          </button>
        </div>
      </div>

      {/* Offline Alert */}
      {!isOnline && (
        <div className="p-3 bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs rounded-xl text-center">
          ⚠️ 目前處於離線狀態，已顯示最近一次載入的暫存資料（可能不是最新資料）。請恢復網路連線以進行新增、修改或刪除操作。
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="flex flex-col md:flex-row gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800/40">
        <div className="flex-1">
          <input
            type="text"
            placeholder="搜尋貨櫃編號、園區、位置..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full glass-input px-4 py-2 rounded-xl text-sm"
          />
        </div>
        
        {/* Status filters */}
        <div className="flex flex-wrap gap-2">
          {['all', 'available', 'rented', 'maintenance', 'retired'].map((status) => {
            const label = status === 'all' ? '全部' : 
                          status === 'available' ? '空櫃' :
                          status === 'rented' ? '出租中' :
                          status === 'maintenance' ? '維修中' : '停用';
            
            const isActive = statusFilter === status;
            
            return (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
                  isActive 
                    ? 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30' 
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                {label}
              </button>
            );
          })}
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : filteredContainers.length === 0 ? (
        <div className="text-center py-20 bg-slate-900/20 border border-slate-850 rounded-2xl">
          <p className="text-slate-500">找不到符合條件的貨櫃。</p>
        </div>
      ) : (
        <>
          {/* PC Table View - Visible on lg screens */}
          <div className="hidden lg:block glass-card rounded-2xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-900/80 text-slate-400 uppercase text-xs border-b border-slate-850">
                  <tr>
                    <th className="px-6 py-4">貨櫃編號</th>
                    <th className="px-6 py-4">規格尺寸</th>
                    <th className="px-6 py-4">種類</th>
                    <th className="px-6 py-4">位置標記</th>
                    <th className="px-6 py-4">購置成本</th>
                    <th className="px-6 py-4">狀態</th>
                    <th className="px-6 py-4">備註</th>
                    <th className="px-6 py-4 text-right">操作</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-850">
                  {filteredContainers.map((c) => (
                    <tr key={c.container_id} className="hover:bg-slate-900/35 transition-colors">
                      <td className="px-6 py-4 font-bold text-white text-base">{c.container_no}</td>
                      <td className="px-6 py-4">{c.size_ft} 呎</td>
                      <td className="px-6 py-4 capitalize">{c.container_type}</td>
                      <td className="px-6 py-4">
                        <span className="bg-slate-900 text-slate-300 px-2 py-1 rounded text-xs">
                          {c.location_zone} - {c.location_label}
                        </span>
                      </td>
                      <td className="px-6 py-4">{formatCurrency(c.total_setup_cost)}</td>
                      <td className="px-6 py-4">{getStatusBadge(c.status)}</td>
                      <td className="px-6 py-4 text-xs text-slate-400 max-w-[150px] truncate" title={c.note}>
                        {c.note || '-'}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex justify-end gap-2">
                          <select
                            value={c.status}
                            onChange={(e) => handleQuickStatusChange(c.container_id, e.target.value as Container['status'])}
                            disabled={!isOnline}
                            className="bg-slate-900 border border-slate-800 text-slate-300 text-xs rounded px-2 py-1"
                          >
                            <option value="available">空櫃</option>
                            <option value="rented">出租中</option>
                            <option value="maintenance">維修中</option>
                            <option value="retired">停用</option>
                          </select>
                          <button
                            onClick={() => handleOpenEdit(c)}
                            disabled={!isOnline}
                            title={isOnline ? undefined : '目前離線，恢復網路後才能儲存'}
                            className="text-xs bg-indigo-950/40 text-indigo-400 border border-indigo-900/50 hover:bg-indigo-900/40 disabled:opacity-50 px-3 py-1.5 rounded-lg transition"
                          >
                            編輯
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Mobile Card View - Hidden on lg screens */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 lg:hidden">
            {filteredContainers.map((c) => (
              <div key={c.container_id} className="glass-card rounded-2xl p-5 space-y-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="text-xl font-bold text-white">{c.container_no}</h4>
                    <p className="text-xs text-slate-500">{c.size_ft} 呎 · {c.container_type}</p>
                  </div>
                  {getStatusBadge(c.status)}
                </div>

                <div className="grid grid-cols-2 gap-3 text-sm border-t border-b border-slate-850 py-3 text-slate-300">
                  <div>
                    <span className="block text-[10px] text-slate-500 font-semibold uppercase">存放位置</span>
                    <span className="font-medium">{c.location_zone} / {c.location_label}</span>
                  </div>
                  <div>
                    <span className="block text-[10px] text-slate-500 font-semibold uppercase">建置成本</span>
                    <span className="font-medium">{formatCurrency(c.total_setup_cost)}</span>
                  </div>
                </div>

                {c.note && (
                  <p className="text-xs text-slate-400 bg-slate-950/40 p-2.5 rounded-lg border border-slate-900/50">
                    備註: {c.note}
                  </p>
                )}

                <div className="flex justify-between items-center pt-2">
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs text-slate-400">快速切換:</span>
                    <select
                      value={c.status}
                      onChange={(e) => handleQuickStatusChange(c.container_id, e.target.value as Container['status'])}
                      disabled={!isOnline}
                      className="bg-slate-900 border border-slate-800 text-slate-300 text-xs rounded px-2 py-1"
                    >
                      <option value="available">空櫃</option>
                      <option value="rented">出租中</option>
                      <option value="maintenance">維修中</option>
                      <option value="retired">停用</option>
                    </select>
                  </div>
                  
                  <button
                    onClick={() => handleOpenEdit(c)}
                    disabled={!isOnline}
                    title={isOnline ? undefined : '目前離線，恢復網路後才能儲存'}
                    className="text-xs bg-indigo-950/40 text-indigo-400 border border-indigo-900/50 hover:bg-indigo-900/40 disabled:opacity-50 px-3.5 py-1.5 rounded-lg transition"
                  >
                    編輯規格
                  </button>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Add / Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-lg rounded-2xl p-6 border border-slate-750 shadow-2xl relative">
            <h3 className="text-xl font-bold text-white mb-4">
              {modalMode === 'create' ? '➕ 新增貨櫃' : '✏️ 編輯貨櫃規格'}
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">貨櫃編號</label>
                  <input
                    type="text"
                    required
                    placeholder="如：A001"
                    value={formData.container_no}
                    onChange={(e) => setFormData({...formData, container_no: e.target.value})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">尺寸 (呎)</label>
                  <select
                    value={formData.size_ft}
                    onChange={(e) => setFormData({...formData, size_ft: parseInt(e.target.value, 10)})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  >
                    <option value={20}>20 呎</option>
                    <option value={40}>40 呎</option>
                    <option value={10}>10 呎</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">貨櫃種類</label>
                  <select
                    value={formData.container_type}
                    onChange={(e) => setFormData({...formData, container_type: e.target.value})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  >
                    <option value="standard">標準乾貨櫃 (Standard)</option>
                    <option value="refrigerated">冷凍櫃 (Reefer)</option>
                    <option value="open_top">開頂櫃 (Open Top)</option>
                    <option value="flat_rack">框架櫃 (Flat Rack)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">初始狀態</label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({...formData, status: e.target.value as Container['status']})}
                    disabled={modalMode === 'edit' && formData.status === 'rented'}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  >
                    <option value="available">空櫃 (Available)</option>
                    <option value="rented" disabled>出租中 (Rented - 需經由合約建立)</option>
                    <option value="maintenance">維修中 (Maintenance)</option>
                    <option value="retired">停用 (Retired)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">存放園區 (Zone)</label>
                  <input
                    type="text"
                    required
                    placeholder="如：A區、B區"
                    value={formData.location_zone}
                    onChange={(e) => setFormData({...formData, location_zone: e.target.value})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">位置編號 (Label)</label>
                  <input
                    type="text"
                    placeholder="如：A-12"
                    value={formData.location_label}
                    onChange={(e) => setFormData({...formData, location_label: e.target.value})}
                    className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">購置/改裝成本 (TWD)</label>
                <input
                  type="number"
                  placeholder="總建置金額"
                  value={formData.total_setup_cost || ''}
                  onChange={(e) => setFormData({...formData, total_setup_cost: parseInt(e.target.value, 10) || 0})}
                  className="w-full glass-input px-3 py-2 rounded-xl text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">備註說明</label>
                <textarea
                  placeholder="貨櫃特徵、損壞紀錄或特別註記..."
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

    </div>
  );
}
