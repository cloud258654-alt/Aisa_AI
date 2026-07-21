import React, { useState, useEffect } from 'react';
import { listContainers, createContainer, updateContainer } from '../services/api/containersApi';
import { Container } from '../types/container';
import PageHeader from '../components/ui/PageHeader';
import DataTable from '../components/ui/DataTable';
import MobileRecordCard from '../components/ui/MobileRecordCard';
import StatusBadge from '../components/ui/StatusBadge';
import SearchFilterBar from '../components/ui/SearchFilterBar';
import LoadingState from '../components/ui/LoadingState';

import { ContainersIcon } from '../components/ui/Icons';
import { exportToCsv } from '../utils/csvExport';

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
    status: 'AVAILABLE' as Container['status'],
    note: ''
  });

  useEffect(() => {
    const online = () => setIsOnline(true);
    const offline = () => setIsOnline(false);
    window.addEventListener('online', online);
    window.addEventListener('offline', offline);

    void loadContainers();

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
      status: 'AVAILABLE',
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
      void loadContainers();
    } catch (err) {
      alert("儲存失敗：" + (err instanceof Error ? err.message : String(err)));
    }
  };

  const filteredContainers = containers.filter((c) => {
    const matchesSearch =
      c.container_no.toLowerCase().includes(search.toLowerCase()) ||
      c.location_label.toLowerCase().includes(search.toLowerCase()) ||
      c.location_zone.toLowerCase().includes(search.toLowerCase());
    const matchesStatus =
      statusFilter === 'all' || (c.status || '').toLowerCase() === statusFilter.toLowerCase();
    return matchesSearch && matchesStatus;
  });

  const handleExportCsv = () => {
    const headers = ['貨櫃編號', '尺寸(呎)', '類型', '存放區域', '定位標籤', '建置成本', '當前狀態', '備註'];
    const rows = filteredContainers.map((c) => [
      c.container_no,
      c.size_ft,
      c.container_type,
      c.location_zone,
      c.location_label || '',
      c.total_setup_cost,
      c.status,
      c.note || ''
    ]);
    exportToCsv('富田貨櫃庫存報表', headers, rows);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="貨櫃倉儲管理"
        description="追蹤全場貨櫃尺寸、區域定位、初始建置成本與狀態流轉。"
        actionButton={
          <div className="flex items-center gap-2">
            <button
              onClick={handleExportCsv}
              className="px-3 py-2 bg-surface-muted hover:bg-border-default text-brand-navy-950 rounded-lg text-xs font-semibold border border-border-default flex items-center gap-1.5 shadow-xs"
            >
              📥 匯出 CSV
            </button>
            <button
              onClick={handleOpenCreate}
              className="px-4 py-2 bg-brand-navy-950 hover:bg-brand-navy-900 text-white rounded-lg text-xs font-semibold shadow-sm flex items-center gap-2"
            >
              <ContainersIcon className="w-4 h-4 text-brand-gold-300" /> 新增貨櫃
            </button>
          </div>
        }
      />

      <SearchFilterBar
        searchValue={search}
        onSearchChange={setSearch}
        placeholder="搜尋貨櫃編號 / 位置標籤..."
        filters={[
          {
            id: 'status',
            label: '狀態',
            value: statusFilter,
            onChange: setStatusFilter,
            options: [
              { value: 'all', label: '全部貨櫃狀態' },
              { value: 'available', label: '空櫃 (AVAILABLE)' },
              { value: 'rented', label: '出租中 (RENTED)' },
              { value: 'inspection', label: '退租檢查中 (INSPECTION)' },
              { value: 'maintenance', label: '維修中 (MAINTENANCE)' },
              { value: 'retired', label: '已停用 (RETIRED)' }
            ]
          }
        ]}
      />

      {loading ? (
        <LoadingState text="載入貨櫃列表數據中..." />
      ) : (
        <>
          <DataTable<Container>
            columns={[
              {
                header: '貨櫃編號',
                accessor: (r) => <span className="font-mono text-xs font-bold text-brand-navy-950">{r.container_no}</span>
              },
              { header: '尺寸規格', accessor: (r) => `${r.size_ft} 呎` },
              { header: '類型', accessor: 'container_type' },
              { header: '存放區域', accessor: (r) => `${r.location_zone} - ${r.location_label || '未標記'}` },
              {
                header: '建置成本',
                accessor: (r) => <span className="font-semibold">${r.total_setup_cost.toLocaleString()}</span>
              },
              {
                header: '當前狀態',
                accessor: (r) => <StatusBadge status={r.status} />
              },
              {
                header: '操作',
                accessor: (r) => (
                  <button
                    onClick={() => handleOpenEdit(r)}
                    className="px-2.5 py-1 text-xs bg-surface-muted hover:bg-brand-navy-950 hover:text-white font-semibold rounded border border-border-default transition-all"
                  >
                    編輯規格
                  </button>
                )
              }
            ]}
            data={filteredContainers}
            keyExtractor={(r) => r.container_id}
            emptyText="目前尚無符合條件的貨櫃資料"
          />

          <div className="md:hidden space-y-3">
            {filteredContainers.map((r) => (
              <MobileRecordCard
                key={r.container_id}
                title={r.container_no}
                subtitle={`${r.size_ft} 呎 / ${r.container_type}`}
                badge={<StatusBadge status={r.status} />}
                fields={[
                  { label: '存放位置', value: `${r.location_zone} (${r.location_label})` },
                  { label: '建置成本', value: `$${r.total_setup_cost.toLocaleString()}` }
                ]}
                actionButtons={
                  <button
                    onClick={() => handleOpenEdit(r)}
                    className="px-3 py-1 text-xs bg-brand-navy-950 text-white font-semibold rounded"
                  >
                    編輯規格
                  </button>
                }
              />
            ))}
          </div>
        </>
      )}

      {/* Add / Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div onClick={() => setIsModalOpen(false)} className="fixed inset-0 bg-brand-navy-950/60 backdrop-blur-xs"></div>
          <div className="relative w-full max-w-lg saas-card p-6 shadow-2xl z-10 space-y-4 animate-fade-in">
            <h3 className="font-bold text-lg text-brand-navy-950">
              {modalMode === 'create' ? '新增貨櫃資料' : `編輯貨櫃 (${formData.container_no})`}
            </h3>

            <form onSubmit={handleSubmit} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-text-secondary mb-1">貨櫃編號</label>
                  <input
                    type="text"
                    required
                    value={formData.container_no}
                    onChange={(e) => setFormData({ ...formData, container_no: e.target.value })}
                    className="w-full saas-input"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-text-secondary mb-1">尺寸 (呎)</label>
                  <input
                    type="number"
                    required
                    value={formData.size_ft}
                    onChange={(e) => setFormData({ ...formData, size_ft: Number(e.target.value) })}
                    className="w-full saas-input"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-text-secondary mb-1">區域 Zone</label>
                  <input
                    type="text"
                    value={formData.location_zone}
                    onChange={(e) => setFormData({ ...formData, location_zone: e.target.value })}
                    className="w-full saas-input"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-text-secondary mb-1">定位 Label</label>
                  <input
                    type="text"
                    value={formData.location_label}
                    onChange={(e) => setFormData({ ...formData, location_label: e.target.value })}
                    className="w-full saas-input"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-text-secondary mb-1">建置成本 ($)</label>
                <input
                  type="number"
                  value={formData.total_setup_cost}
                  onChange={(e) => setFormData({ ...formData, total_setup_cost: Number(e.target.value) })}
                  className="w-full saas-input"
                />
              </div>

              <div>
                <label className="block font-semibold text-text-secondary mb-1">貨櫃狀態</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value as Container['status'] })}
                  disabled={modalMode === 'edit' && (formData.status === 'rented' || formData.status === 'RENTED')}
                  className="w-full saas-input"
                >
                  <option value="AVAILABLE">空櫃 (AVAILABLE)</option>
                  <option value="RENTED" disabled>出租中 (RENTED - 需由合約控制)</option>
                  <option value="INSPECTION" disabled>退租檢查中 (INSPECTION - 需由驗收控制)</option>
                  <option value="MAINTENANCE">維修中 (MAINTENANCE)</option>
                  <option value="RETIRED">已停用 (RETIRED)</option>
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold text-text-secondary hover:bg-surface-muted rounded-lg border border-border-default"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-brand-navy-950 hover:bg-brand-navy-900 text-white font-semibold text-xs rounded-lg shadow-sm"
                >
                  確認儲存
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
