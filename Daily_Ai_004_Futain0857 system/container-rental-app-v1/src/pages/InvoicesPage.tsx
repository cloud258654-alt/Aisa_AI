import React, { useState, useEffect } from 'react';
import { Invoice } from '../types/invoice';
import { fetchInvoices, createInvoice } from '../services/api/invoicesApi';
import { createPayment, voidPayment } from '../services/api/paymentsApi';
import PageHeader from '../components/ui/PageHeader';
import DataTable from '../components/ui/DataTable';
import MobileRecordCard from '../components/ui/MobileRecordCard';
import StatusBadge from '../components/ui/StatusBadge';
import SearchFilterBar from '../components/ui/SearchFilterBar';
import LoadingState from '../components/ui/LoadingState';
import ErrorState from '../components/ui/ErrorState';
import ConfirmDialog from '../components/ui/ConfirmDialog';
import { exportToCsv } from '../utils/csvExport';

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const [selectedInvoiceId, setSelectedInvoiceId] = useState('');
  const [payAmount, setPayAmount] = useState('10000');
  const [payMethod, setPayMethod] = useState<'cash' | 'bank_transfer' | 'line_pay' | 'check'>('bank_transfer');

  const [newCustId, setNewCustId] = useState('');
  const [newAmountDue, setNewAmountDue] = useState('24000');

  const [voidTargetId, setVoidTargetId] = useState<string | null>(null);

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
      alert('應收帳單開立成功！');
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
        requestId: 'REQ-PAY-' + Date.now(),
        invoice_id: selectedInvoiceId,
        customer_id: inv.customer_id,
        payment_type: 'rent',
        payment_method: payMethod,
        payment_date: new Date().toISOString().split('T')[0],
        amount: Number(payAmount)
      });
      alert('收款成功紀錄！餘額已動態對帳更新。');
      void loadData();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : '收款失敗');
    }
  };

  const handleConfirmVoid = async () => {
    if (!voidTargetId) return;
    try {
      await voidPayment(voidTargetId, '人工作廢作業');
      alert('付款紀錄已成功作廢！已自動重新計算帳單餘額。');
      setVoidTargetId(null);
      void loadData();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : '作廢失敗');
    }
  };

  const filteredInvoices = invoices.filter((inv) => {
    const matchesSearch =
      inv.invoice_no.toLowerCase().includes(search.toLowerCase()) ||
      inv.customer_id.toLowerCase().includes(search.toLowerCase());
    const matchesStatus =
      statusFilter === 'ALL' || (inv.status || '').toUpperCase() === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleExportCsv = () => {
    const headers = ['帳單單號', '客戶ID', '合約ID', '應收金額', '已付金額', '剩餘未付', '到期日期', '狀態'];
    const rows = filteredInvoices.map((inv) => [
      inv.invoice_no,
      inv.customer_id,
      inv.contract_id || '',
      inv.amount_due,
      inv.amount_paid,
      inv.balance_due,
      inv.due_date,
      inv.status
    ]);
    exportToCsv('福田應收與對帳報表', headers, rows);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="應收與收款對帳管理"
        description="開立租金與押金應收帳單、登記部分或全額對帳付款，以及作廢與餘額動態計算。"
        actionButton={
          <button
            onClick={handleExportCsv}
            className="px-4 py-2 bg-brand-navy-950 hover:bg-brand-navy-900 text-white rounded-lg text-xs font-semibold shadow-sm flex items-center gap-2"
          >
            <span>📥</span> 匯出 CSV 報表
          </button>
        }
      />

      {/* Quick Action Forms */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <form onSubmit={handleCreateInvoice} className="saas-card p-5 space-y-4">
          <h3 className="font-bold text-base text-brand-navy-950 border-b border-border-default pb-2">
            1. 開立應收帳單
          </h3>
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1">客戶 ID</label>
              <input
                type="text"
                placeholder="例如 CUST-001"
                value={newCustId}
                onChange={(e) => setNewCustId(e.target.value)}
                className="w-full saas-input"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1">應收金額 ($)</label>
              <input
                type="number"
                placeholder="例如 24000"
                value={newAmountDue}
                onChange={(e) => setNewAmountDue(e.target.value)}
                className="w-full saas-input"
                required
              />
            </div>
          </div>
          <button type="submit" className="w-full py-2 bg-brand-navy-950 text-white font-semibold text-xs rounded-lg shadow-sm">
            開立帳單
          </button>
        </form>

        <form onSubmit={handleRecordPayment} className="saas-card p-5 space-y-4">
          <h3 className="font-bold text-base text-brand-navy-950 border-b border-border-default pb-2">
            2. 登記對帳收款 (支援部分付款)
          </h3>
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1">選擇繳款帳單</label>
              <select
                value={selectedInvoiceId}
                onChange={(e) => setSelectedInvoiceId(e.target.value)}
                className="w-full saas-input text-xs font-medium"
              >
                <option value="">-- 請選擇應收帳單 --</option>
                {invoices.map((inv) => (
                  <option key={inv.invoice_id} value={inv.invoice_id}>
                    {inv.invoice_no} | 應收:${inv.amount_due} | 餘額:${inv.balance_due} ({(inv.status || '').toUpperCase()})
                  </option>
                ))}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1">實收金額 ($)</label>
                <input
                  type="number"
                  placeholder="實收金額"
                  value={payAmount}
                  onChange={(e) => setPayAmount(e.target.value)}
                  className="w-full saas-input"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1">付款管道</label>
                <select
                  value={payMethod}
                  onChange={(e) => setPayMethod(e.target.value as 'cash' | 'bank_transfer' | 'line_pay' | 'check')}
                  className="w-full saas-input text-xs"
                >
                  <option value="bank_transfer">銀行轉帳</option>
                  <option value="cash">現金支付</option>
                  <option value="line_pay">LINE Pay</option>
                </select>
              </div>
            </div>
          </div>
          <button type="submit" className="w-full py-2 bg-status-success text-white font-semibold text-xs rounded-lg shadow-sm">
            登記入帳
          </button>
        </form>
      </div>

      {/* Filter Bar */}
      <SearchFilterBar
        searchValue={search}
        onSearchChange={setSearch}
        placeholder="搜尋帳單單號 / 客戶 ID..."
        filters={[
          {
            id: 'status',
            label: '狀態',
            value: statusFilter,
            onChange: setStatusFilter,
            options: [
              { value: 'ALL', label: '全部帳單狀態' },
              { value: 'UNPAID', label: '未付款 (UNPAID)' },
              { value: 'PARTIAL', label: '部分付款 (PARTIAL)' },
              { value: 'PAID', label: '已結清 (PAID)' },
              { value: 'VOID', label: '已作廢 (VOID)' }
            ]
          }
        ]}
      />

      {error && <ErrorState message={error} onRetry={() => void loadData()} />}

      {loading ? (
        <LoadingState text="載入帳單數據中..." />
      ) : (
        <>
          {/* Desktop Table View */}
          <DataTable<Invoice>
            columns={[
              {
                header: '帳單單號',
                accessor: (r) => <span className="font-mono text-xs font-bold text-brand-navy-950">{r.invoice_no}</span>
              },
              { header: '客戶 ID', accessor: 'customer_id' },
              {
                header: '應收金額',
                accessor: (r) => <span className="font-semibold">${r.amount_due.toLocaleString()}</span>
              },
              {
                header: '已付金額',
                accessor: (r) => <span className="font-semibold text-status-success">${r.amount_paid.toLocaleString()}</span>
              },
              {
                header: '剩餘未付',
                accessor: (r) => <span className="font-bold text-status-danger">${r.balance_due.toLocaleString()}</span>
              },
              {
                header: '帳單狀態',
                accessor: (r) => <StatusBadge status={r.status} />
              },
              {
                header: '操作',
                accessor: (r) => (
                  <button
                    onClick={() => setVoidTargetId(r.invoice_id)}
                    className="px-2.5 py-1 text-xs bg-surface-muted hover:bg-rose-100 text-status-danger font-semibold rounded border border-border-default transition-all"
                  >
                    作廢付款
                  </button>
                )
              }
            ]}
            data={filteredInvoices}
            keyExtractor={(r) => r.invoice_id}
            emptyText="目前尚無符合條件的應收帳單"
          />

          {/* Mobile Card View */}
          <div className="md:hidden space-y-3">
            {filteredInvoices.map((r) => (
              <MobileRecordCard
                key={r.invoice_id}
                title={r.invoice_no}
                subtitle={`客戶: ${r.customer_id}`}
                badge={<StatusBadge status={r.status} />}
                fields={[
                  { label: '應收金額', value: `$${r.amount_due.toLocaleString()}` },
                  { label: '已付金額', value: `$${r.amount_paid.toLocaleString()}` },
                  { label: '剩餘未付', value: `$${r.balance_due.toLocaleString()}` },
                  { label: '到期日', value: r.due_date }
                ]}
                actionButtons={
                  <button
                    onClick={() => setVoidTargetId(r.invoice_id)}
                    className="px-3 py-1 text-xs bg-status-danger text-white font-semibold rounded"
                  >
                    作廢紀錄
                  </button>
                }
              />
            ))}
          </div>
        </>
      )}

      {/* Confirmation Dialog for Voiding */}
      <ConfirmDialog
        isOpen={voidTargetId !== null}
        title="確認作廢付款紀錄"
        message="警告：作廢付款紀錄將無法復原。系統將自動從帳單已付金額扣除該筆金額，並動態重新計算剩餘未付餘額。"
        confirmText="確認作廢"
        isDangerous={true}
        onConfirm={() => void handleConfirmVoid()}
        onCancel={() => setVoidTargetId(null)}
      />
    </div>
  );
}
