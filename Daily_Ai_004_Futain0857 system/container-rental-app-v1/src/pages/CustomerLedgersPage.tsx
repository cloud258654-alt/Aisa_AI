import { useState, useEffect } from 'react';
import { listCustomerLedgers } from '../services/api/customerLedgersApi';
import { CustomerLedger } from '../types/customerLedger';
import PageHeader from '../components/ui/PageHeader';
import DataTable from '../components/ui/DataTable';
import MobileRecordCard from '../components/ui/MobileRecordCard';
import StatusBadge from '../components/ui/StatusBadge';
import SearchFilterBar from '../components/ui/SearchFilterBar';
import LoadingState from '../components/ui/LoadingState';

export default function CustomerLedgersPage() {
  const [ledgers, setLedgers] = useState<CustomerLedger[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const data = await listCustomerLedgers();
        setLedgers(data);
      } catch (err) {
        console.error('Failed to load customer ledgers:', err);
      } finally {
        setLoading(false);
      }
    }
    void loadData();
  }, []);

  const filteredLedgers = ledgers.filter((l) =>
    l.customer_id.toLowerCase().includes(search.toLowerCase()) ||
    (l.note || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="客戶帳務對帳紀錄 (Legacy Ledger)"
        description="檢視傳統客戶對帳單、發票開立狀態與應收應付紀錄。"
      />

      <SearchFilterBar
        searchValue={search}
        onSearchChange={setSearch}
        placeholder="搜尋客戶 ID / 備註說明..."
      />

      {loading ? (
        <LoadingState text="載入客戶帳務資料中..." />
      ) : (
        <>
          <DataTable<CustomerLedger>
            columns={[
              {
                header: '對帳單 ID',
                accessor: (r) => <span className="font-mono text-xs font-bold text-brand-navy-950">{r.ledger_id}</span>
              },
              { header: '客戶 ID', accessor: 'customer_id' },
              { header: '費用類別', accessor: 'event_type' },
              { header: '到期日期', accessor: 'due_date' },
              {
                header: '交易金額',
                accessor: (r) => <span className="font-semibold">${r.amount.toLocaleString()}</span>
              },
              {
                header: '狀態',
                accessor: (r) => <StatusBadge status={r.paid_status} />
              }
            ]}
            data={filteredLedgers}
            keyExtractor={(r) => r.ledger_id}
            emptyText="無傳統客戶帳務資料"
          />

          <div className="md:hidden space-y-3">
            {filteredLedgers.map((r) => (
              <MobileRecordCard
                key={r.ledger_id}
                title={r.ledger_id}
                subtitle={`客戶: ${r.customer_id} (${r.event_type})`}
                badge={<StatusBadge status={r.paid_status} />}
                fields={[
                  { label: '到期日期', value: r.due_date },
                  { label: '交易金額', value: `$${r.amount.toLocaleString()}` }
                ]}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
