import React, { useState, useEffect } from 'react';
import { listManagementLedgers, createManagementLedgerEntry } from '../services/api/managementLedgersApi';
import { ManagementLedger } from '../types/managementLedger';
import PageHeader from '../components/ui/PageHeader';
import DataTable from '../components/ui/DataTable';
import MobileRecordCard from '../components/ui/MobileRecordCard';
import StatusBadge from '../components/ui/StatusBadge';
import SearchFilterBar from '../components/ui/SearchFilterBar';
import LoadingState from '../components/ui/LoadingState';
import { exportToCsv } from '../utils/csvExport';

export default function ManagementLedgersPage() {
  const [ledgers, setLedgers] = useState<ManagementLedger[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const [category, setCategory] = useState<'maintenance' | 'land_rent' | 'utilities' | 'other'>('land_rent');
  const [amount, setAmount] = useState('10000');
  const [desc, setDesc] = useState('');

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await listManagementLedgers();
      setLedgers(data);
    } catch (err) {
      console.error('Failed to load management ledgers:', err);
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
      await createManagementLedgerEntry({
        expense_type: category,
        vendor: '廠商',
        amount: Number(amount),
        paid_status: 'paid',
        record_date: new Date().toISOString().split('T')[0],
        due_date: new Date().toISOString().split('T')[0],
        paid_date: new Date().toISOString().split('T')[0],
        payment_method: 'bank_transfer',
        receipt_no: '',
        is_capitalized: false,
        issue_desc: desc
      });
      alert('營運支出新增成功！');
      setDesc('');
      void loadData();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : '建立失敗');
    }
  };

  const filteredLedgers = ledgers.filter((l) =>
    (l.expense_type || '').toLowerCase().includes(search.toLowerCase()) ||
    (l.issue_desc || '').toLowerCase().includes(search.toLowerCase())
  );

  const handleExportCsv = () => {
    const headers = ['紀錄ID', '貨櫃ID', '支出類別', '廠商名稱', '金額', '付款狀態', '紀錄日期', '付款方式', '說明敘述'];
    const rows = filteredLedgers.map((l) => [
      l.ledger_id,
      l.container_id || '',
      l.expense_type,
      l.vendor || '',
      l.amount,
      l.paid_status,
      l.record_date,
      l.payment_method || '',
      l.issue_desc || ''
    ]);
    exportToCsv('富田營運支出紀錄報表', headers, rows);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="營運支出與場地費用管理"
        description="登記場地租金、地租、水電雜支與貨櫃修繕營運支出。"
        actionButton={
          <button
            onClick={handleExportCsv}
            className="px-4 py-2 bg-brand-navy-950 hover:bg-brand-navy-900 text-white rounded-lg text-xs font-semibold shadow-sm flex items-center gap-2"
          >
            <span>📥</span> 匯出 CSV 報表
          </button>
        }
      />

      {/* Add Expense Form */}
      <form onSubmit={handleCreate} className="saas-card p-5 space-y-4">
        <h3 className="font-bold text-base text-brand-navy-950 border-b border-border-default pb-2">
          登記營運支出
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div>
            <label className="block font-semibold text-text-secondary mb-1">支出類別</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value as 'land_rent' | 'maintenance' | 'utilities' | 'other')}
              className="w-full saas-input"
            >
              <option value="land_rent">場地地租 (Land Rent)</option>
              <option value="maintenance">維修保養 (Maintenance)</option>
              <option value="utilities">水電電費 (Utilities)</option>
              <option value="other">其他雜支 (Other)</option>
            </select>
          </div>
          <div>
            <label className="block font-semibold text-text-secondary mb-1">金額 ($)</label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full saas-input"
              required
            />
          </div>
          <div>
            <label className="block font-semibold text-text-secondary mb-1">說明敘述</label>
            <input
              type="text"
              placeholder="例如 7 月份地租"
              value={desc}
              onChange={(e) => setDesc(e.target.value)}
              className="w-full saas-input"
            />
          </div>
        </div>
        <button type="submit" className="px-5 py-2 bg-brand-navy-950 text-white font-semibold text-xs rounded-lg shadow-sm">
          登記入帳
        </button>
      </form>

      <SearchFilterBar
        searchValue={search}
        onSearchChange={setSearch}
        placeholder="搜尋支出類別 / 說明敘述..."
      />

      {loading ? (
        <LoadingState text="載入營運支出資料中..." />
      ) : (
        <>
          <DataTable<ManagementLedger>
            columns={[
              {
                header: '支出紀錄 ID',
                accessor: (r) => <span className="font-mono text-xs font-bold text-brand-navy-950">{r.ledger_id}</span>
              },
              { header: '支出類別', accessor: 'expense_type' },
              { header: '支出日期', accessor: 'record_date' },
              {
                header: '金額',
                accessor: (r) => <span className="font-bold text-brand-navy-950">${r.amount.toLocaleString()}</span>
              },
              { header: '說明敘述', accessor: (r) => r.issue_desc || '無' },
              {
                header: '付款狀態',
                accessor: (r) => <StatusBadge status={r.paid_status} />
              }
            ]}
            data={filteredLedgers}
            keyExtractor={(r) => r.ledger_id}
            emptyText="目前尚無營運支出紀錄"
          />

          <div className="md:hidden space-y-3">
            {filteredLedgers.map((r) => (
              <MobileRecordCard
                key={r.ledger_id}
                title={r.expense_type}
                subtitle={`日期: ${r.record_date}`}
                badge={<StatusBadge status={r.paid_status} />}
                fields={[
                  { label: '支出金額', value: `$${r.amount.toLocaleString()}` },
                  { label: '說明敘述', value: r.issue_desc || '無' }
                ]}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
