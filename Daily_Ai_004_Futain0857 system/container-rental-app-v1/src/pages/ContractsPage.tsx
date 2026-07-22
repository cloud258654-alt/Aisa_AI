import { useState, useEffect } from 'react';
import { Contract } from '../types/contract';
import { fetchContracts, renewContract } from '../services/api/contractsApi';
import PageHeader from '../components/ui/PageHeader';
import DataTable from '../components/ui/DataTable';
import MobileRecordCard from '../components/ui/MobileRecordCard';
import StatusBadge from '../components/ui/StatusBadge';
import SearchFilterBar from '../components/ui/SearchFilterBar';
import LoadingState from '../components/ui/LoadingState';
import ErrorState from '../components/ui/ErrorState';
import ContractWizard from '../components/contracts/ContractWizard';
import ConfirmDialog from '../components/ui/ConfirmDialog';
import { ContractsIcon } from '../components/ui/Icons';
import { exportToCsv } from '../utils/csvExport';

export default function ContractsPage() {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [isWizardOpen, setIsWizardOpen] = useState(false);

  const [renewTargetId, setRenewTargetId] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchContracts();
      setContracts(data);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : '載入合約資料失敗');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadData();
  }, []);

  const handleConfirmRenew = async () => {
    if (!renewTargetId) return;
    try {
      await renewContract({
        requestId: 'REQ-RENEW-' + Date.now(),
        previous_contract_id: renewTargetId,
        start_date: new Date().toISOString().split('T')[0],
        rent_total: 48000,
        deposit_total: 0,
        installment_count: 2,
        items: [
          {
            container_id: 'CONT-001',
            unit_price: 48000,
            discount_amount: 0,
            effective_price: 48000,
            start_date: new Date().toISOString().split('T')[0],
            status: 'ACTIVE'
          }
        ]
      });
      alert('合約續約成功！已關聯原合約並產生新一期應收。');
      setRenewTargetId(null);
      void loadData();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : '續約失敗');
    }
  };

  const filteredContracts = contracts.filter((c) => {
    const matchesSearch =
      c.contract_no.toLowerCase().includes(search.toLowerCase()) ||
      c.customer_id.toLowerCase().includes(search.toLowerCase());
    const matchesStatus =
      statusFilter === 'ALL' || (c.status || '').toUpperCase() === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleExportCsv = () => {
    const headers = ['合約編號', '合約ID', '客戶ID', '起租日期', '結束日期', '租金總額', '押金總額', '分期數', '狀態'];
    const rows = filteredContracts.map((c) => [
      c.contract_no,
      c.contract_id,
      c.customer_id,
      c.start_date,
      c.end_date || '',
      c.rent_total,
      c.deposit_total,
      c.installment_count,
      c.status
    ]);
    exportToCsv('福田租賃合約清單報表', headers, rows);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="租約與合約管理"
        description="管理貨櫃承租合約啟用、多櫃合約關聯、分期租金帳單與合約續約辦理。"
        actionButton={
          <div className="flex items-center gap-2">
            <button
              onClick={handleExportCsv}
              className="px-3 py-2 bg-surface-muted hover:bg-border-default text-brand-navy-950 rounded-lg text-xs font-semibold border border-border-default flex items-center gap-1.5 shadow-xs"
            >
              📥 匯出 CSV
            </button>
            <button
              onClick={() => setIsWizardOpen(true)}
              className="px-4 py-2 bg-brand-navy-950 hover:bg-brand-navy-900 text-white rounded-lg text-xs font-semibold shadow-sm flex items-center gap-2"
            >
              <ContractsIcon className="w-4 h-4 text-brand-gold-300" /> 建立新合約 (Wizard)
            </button>
          </div>
        }
      />

      {/* Contract Creation Wizard Modal */}
      {isWizardOpen && (
        <div className="mb-6">
          <ContractWizard
            onSuccess={() => {
              setIsWizardOpen(false);
              void loadData();
            }}
            onCancel={() => setIsWizardOpen(false)}
          />
        </div>
      )}

      {/* Search & Filter Bar */}
      <SearchFilterBar
        searchValue={search}
        onSearchChange={setSearch}
        placeholder="搜尋合約編號 / 客戶 ID..."
        filters={[
          {
            id: 'status',
            label: '狀態',
            value: statusFilter,
            onChange: setStatusFilter,
            options: [
              { value: 'ALL', label: '全部合約狀態' },
              { value: 'ACTIVE', label: '生效中 (ACTIVE)' },
              { value: 'ENDING', label: '退租中 (ENDING)' },
              { value: 'ENDED', label: '已結束 (ENDED)' }
            ]
          }
        ]}
      />

      {error && <ErrorState message={error} onRetry={() => void loadData()} />}

      {loading ? (
        <LoadingState text="載入合約清單中..." />
      ) : (
        <>
          {/* Desktop Table View */}
          <DataTable<Contract>
            columns={[
              {
                header: '合約編號',
                accessor: (r) => (
                  <span className="font-mono text-xs font-bold text-brand-navy-950">{r.contract_no}</span>
                )
              },
              { header: '客戶 ID', accessor: 'customer_id' },
              { header: '起租日期', accessor: 'start_date' },
              {
                header: '租金總額',
                accessor: (r) => <span className="font-semibold">${r.rent_total.toLocaleString()}</span>
              },
              {
                header: '押金總額',
                accessor: (r) => <span className="font-semibold text-amber-700">${r.deposit_total.toLocaleString()}</span>
              },
              { header: '分期', accessor: (r) => `${r.installment_count} 期` },
              {
                header: '合約狀態',
                accessor: (r) => <StatusBadge status={r.status} />
              },
              {
                header: '操作',
                accessor: (r) => (
                  <div className="flex items-center gap-2">
                    {((r.status || '').toUpperCase() === 'ACTIVE' || (r.status || '').toUpperCase() === 'ENDED') && (
                      <button
                        onClick={() => setRenewTargetId(r.contract_id)}
                        className="px-2.5 py-1 text-xs bg-surface-muted hover:bg-brand-gold-500/20 text-brand-navy-950 font-semibold rounded border border-border-default transition-all"
                      >
                        辦理續約
                      </button>
                    )}
                  </div>
                )
              }
            ]}
            data={filteredContracts}
            keyExtractor={(r) => r.contract_id}
            emptyText="目前尚無符合條件的合約紀錄"
          />

          {/* Mobile Card View */}
          <div className="md:hidden space-y-3">
            {filteredContracts.map((r) => (
              <MobileRecordCard
                key={r.contract_id}
                title={r.contract_no}
                subtitle={`客戶: ${r.customer_id}`}
                badge={<StatusBadge status={r.status} />}
                fields={[
                  { label: '起租日期', value: r.start_date },
                  { label: '租金金額', value: `$${r.rent_total.toLocaleString()}` },
                  { label: '押金金額', value: `$${r.deposit_total.toLocaleString()}` },
                  { label: '分期數', value: `${r.installment_count} 期` }
                ]}
                actionButtons={
                  ((r.status || '').toUpperCase() === 'ACTIVE' || (r.status || '').toUpperCase() === 'ENDED') && (
                    <button
                      onClick={() => setRenewTargetId(r.contract_id)}
                      className="px-3 py-1 text-xs bg-brand-navy-950 text-white font-semibold rounded"
                    >
                      辦理續約
                    </button>
                  )
                }
              />
            ))}
          </div>
        </>
      )}

      {/* Confirmation Dialog for Renewal */}
      <ConfirmDialog
        isOpen={renewTargetId !== null}
        title="確認辦理合約續約"
        message={`您即將為合約 (${renewTargetId}) 辦理續約手續。續約將保留舊合約完整歷史，並建立連動之新合約與新一期應收帳單。`}
        confirmText="確認續約"
        isDangerous={false}
        onConfirm={() => void handleConfirmRenew()}
        onCancel={() => setRenewTargetId(null)}
      />
    </div>
  );
}
