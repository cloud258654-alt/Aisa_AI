import React, { useState, useEffect } from 'react';
import { listCustomers, createCustomer, updateCustomer } from '../services/api/customersApi';
import { Customer } from '../types/customer';
import PageHeader from '../components/ui/PageHeader';
import DataTable from '../components/ui/DataTable';
import MobileRecordCard from '../components/ui/MobileRecordCard';
import StatusBadge from '../components/ui/StatusBadge';
import SearchFilterBar from '../components/ui/SearchFilterBar';
import LoadingState from '../components/ui/LoadingState';
import { UsersIcon } from '../components/ui/Icons';
import { exportToCsv } from '../utils/csvExport';

export default function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<'create' | 'edit'>('create');
  const [editingId, setEditingId] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    name: '',
    customer_type: 'personal' as 'personal' | 'business',
    tax_id: '',
    phone: '',
    email: '',
    billing_address: '',
    status: 'ACTIVE' as 'ACTIVE' | 'INACTIVE' | 'active' | 'inactive',
    note: ''
  });

  useEffect(() => {
    void loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await listCustomers();
      setCustomers(data);
    } catch (err) {
      console.error("Failed to load customers:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenCreate = () => {
    setModalMode('create');
    setEditingId(null);
    setFormData({
      name: '',
      customer_type: 'personal',
      tax_id: '',
      phone: '',
      email: '',
      billing_address: '',
      status: 'ACTIVE',
      note: ''
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (cust: Customer) => {
    setModalMode('edit');
    setEditingId(cust.customer_id);
    setFormData({
      name: cust.name,
      customer_type: cust.customer_type,
      tax_id: cust.tax_id || '',
      phone: cust.phone,
      email: cust.email || '',
      billing_address: cust.billing_address || '',
      status: cust.status as 'ACTIVE' | 'INACTIVE',
      note: cust.note || ''
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim() || !formData.phone.trim()) {
      return alert("請填寫姓名與電話");
    }

    try {
      const payload = {
        ...formData,
        line_id: ''
      };
      if (modalMode === 'create') {
        await createCustomer(payload);
      } else if (editingId) {
        await updateCustomer(editingId, payload);
      }
      setIsModalOpen(false);
      void loadData();
    } catch (err) {
      alert("儲存失敗：" + (err instanceof Error ? err.message : String(err)));
    }
  };

  const filteredCustomers = customers.filter((c) => {
    const matchesSearch =
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.phone.includes(search) ||
      (c.tax_id || '').includes(search);
    const matchesStatus =
      statusFilter === 'ALL' || (c.status || '').toUpperCase() === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleExportCsv = () => {
    const headers = ['客戶ID', '客戶名稱', '客戶類型', '聯絡電話', '統一編號', '電子信箱', '通訊地址', '狀態'];
    const rows = filteredCustomers.map((c) => [
      c.customer_id,
      c.name,
      c.customer_type === 'business' ? '企業' : '個人',
      c.phone,
      c.tax_id || '',
      c.email || '',
      c.billing_address || '',
      c.status
    ]);
    exportToCsv('富田客戶名冊報表', headers, rows);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="客戶資料管理"
        description="維護個人與企業租客聯絡資訊、統一編號、發票寄送地址與狀態控管。"
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
              <UsersIcon className="w-4 h-4 text-brand-gold-300" /> 新增客戶
            </button>
          </div>
        }
      />

      <SearchFilterBar
        searchValue={search}
        onSearchChange={setSearch}
        placeholder="搜尋姓名 / 電話 / 統一編號..."
        filters={[
          {
            id: 'status',
            label: '狀態',
            value: statusFilter,
            onChange: setStatusFilter,
            options: [
              { value: 'ALL', label: '全部客戶狀態' },
              { value: 'ACTIVE', label: '正常 (ACTIVE)' },
              { value: 'INACTIVE', label: '停用 (INACTIVE)' }
            ]
          }
        ]}
      />

      {loading ? (
        <LoadingState text="載入客戶數據中..." />
      ) : (
        <>
          <DataTable<Customer>
            columns={[
              {
                header: '客戶姓名 / 名稱',
                accessor: (r) => <span className="font-bold text-brand-navy-950">{r.name}</span>
              },
              {
                header: '客戶類型',
                accessor: (r) => (r.customer_type === 'business' ? '企業 (Business)' : '個人 (Personal)')
              },
              { header: '聯絡電話', accessor: 'phone' },
              { header: '統一編號', accessor: (r) => r.tax_id || '無' },
              { header: '電子信箱', accessor: (r) => r.email || '無' },
              {
                header: '客戶狀態',
                accessor: (r) => <StatusBadge status={r.status} />
              },
              {
                header: '操作',
                accessor: (r) => (
                  <button
                    onClick={() => handleOpenEdit(r)}
                    className="px-2.5 py-1 text-xs bg-surface-muted hover:bg-brand-navy-950 hover:text-white font-semibold rounded border border-border-default transition-all"
                  >
                    編輯客戶
                  </button>
                )
              }
            ]}
            data={filteredCustomers}
            keyExtractor={(r) => r.customer_id}
            emptyText="目前尚無符合條件的客戶資料"
          />

          <div className="md:hidden space-y-3">
            {filteredCustomers.map((r) => (
              <MobileRecordCard
                key={r.customer_id}
                title={r.name}
                subtitle={`電話: ${r.phone}`}
                badge={<StatusBadge status={r.status} />}
                fields={[
                  { label: '客戶類型', value: r.customer_type === 'business' ? '企業' : '個人' },
                  { label: '統一編號', value: r.tax_id || '無' },
                  { label: '電子信箱', value: r.email || '無' },
                  { label: '通訊地址', value: r.billing_address || '無' }
                ]}
                actionButtons={
                  <button
                    onClick={() => handleOpenEdit(r)}
                    className="px-3 py-1 text-xs bg-brand-navy-950 text-white font-semibold rounded"
                  >
                    編輯
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
          <div className="relative w-full max-w-md saas-card p-6 shadow-2xl z-10 space-y-4 animate-fade-in">
            <h3 className="font-bold text-lg text-brand-navy-950">
              {modalMode === 'create' ? '新增客戶資料' : `編輯客戶 (${formData.name})`}
            </h3>

            <form onSubmit={handleSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-text-secondary mb-1">客戶姓名 / 公司名稱</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full saas-input"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-text-secondary mb-1">客戶類型</label>
                  <select
                    value={formData.customer_type}
                    onChange={(e) => setFormData({ ...formData, customer_type: e.target.value as 'personal' | 'business' })}
                    className="w-full saas-input"
                  >
                    <option value="personal">個人客戶</option>
                    <option value="business">企業公司</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-text-secondary mb-1">統一編號</label>
                  <input
                    type="text"
                    value={formData.tax_id}
                    onChange={(e) => setFormData({ ...formData, tax_id: e.target.value })}
                    className="w-full saas-input"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-text-secondary mb-1">聯絡電話</label>
                  <input
                    type="text"
                    required
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full saas-input"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-text-secondary mb-1">客戶狀態</label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value as 'ACTIVE' | 'INACTIVE' })}
                    className="w-full saas-input"
                  >
                    <option value="ACTIVE font-semibold text-status-success">正常 (ACTIVE)</option>
                    <option value="INACTIVE">停用 (INACTIVE - 禁止新建約)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-semibold text-text-secondary mb-1">電子信箱</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full saas-input"
                />
              </div>

              <div>
                <label className="block font-semibold text-text-secondary mb-1">帳單與發票地址</label>
                <input
                  type="text"
                  value={formData.billing_address}
                  onChange={(e) => setFormData({ ...formData, billing_address: e.target.value })}
                  className="w-full saas-input"
                />
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
