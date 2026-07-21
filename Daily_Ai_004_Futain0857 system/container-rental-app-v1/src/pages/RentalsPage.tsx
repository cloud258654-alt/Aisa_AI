import { useState, useEffect } from 'react';
import { listRentals } from '../services/api/rentalsApi';
import { listCustomers } from '../services/api/customersApi';
import { listContainers } from '../services/api/containersApi';
import { RentalRecord } from '../types/rentalRecord';
import PageHeader from '../components/ui/PageHeader';
import DataTable from '../components/ui/DataTable';
import MobileRecordCard from '../components/ui/MobileRecordCard';
import StatusBadge from '../components/ui/StatusBadge';
import SearchFilterBar from '../components/ui/SearchFilterBar';
import LoadingState from '../components/ui/LoadingState';

export default function RentalsPage() {
  const [rentals, setRentals] = useState<Array<RentalRecord & { customerName?: string; containerNo?: string }>>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [rentalData, customers, containers] = await Promise.all([
          listRentals(),
          listCustomers(),
          listContainers()
        ]);

        const enriched = rentalData.map((r) => {
          const cust = customers.find((c) => c.customer_id === r.customer_id);
          const cont = containers.find((c) => c.container_id === r.container_id);
          return {
            ...r,
            customerName: cust ? cust.name : '未知客戶',
            containerNo: cont ? cont.container_no : '未知貨櫃'
          };
        });

        setRentals(enriched);
      } catch (err) {
        console.error('Failed to load rentals:', err);
      } finally {
        setLoading(false);
      }
    }
    void loadData();
  }, []);

  const filteredRentals = rentals.filter((r) =>
    (r.customerName || '').toLowerCase().includes(search.toLowerCase()) ||
    (r.containerNo || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="傳統租約紀錄 (Legacy View)"
        description="相容相應歷史傳統單櫃租賃紀錄總覽。"
      />

      <SearchFilterBar
        searchValue={search}
        onSearchChange={setSearch}
        placeholder="搜尋客戶姓名 / 貨櫃編號..."
      />

      {loading ? (
        <LoadingState text="載入傳統租約資料中..." />
      ) : (
        <>
          <DataTable<RentalRecord & { customerName?: string; containerNo?: string }>
            columns={[
              {
                header: '租約 ID',
                accessor: (r) => <span className="font-mono text-xs font-bold text-brand-navy-950">{r.rental_id}</span>
              },
              { header: '客戶', accessor: (r) => r.customerName || r.customer_id },
              { header: '貨櫃編號', accessor: (r) => r.containerNo || r.container_id },
              { header: '起租日期', accessor: 'start_date' },
              { header: '結束日期', accessor: (r) => r.end_date || '長期' },
              {
                header: '月租金',
                accessor: (r) => <span className="font-semibold">${r.monthly_rent.toLocaleString()}</span>
              },
              {
                header: '狀態',
                accessor: (r) => <StatusBadge status={r.status} />
              }
            ]}
            data={filteredRentals}
            keyExtractor={(r) => r.rental_id}
            emptyText="無傳統租約資料"
          />

          <div className="md:hidden space-y-3">
            {filteredRentals.map((r) => (
              <MobileRecordCard
                key={r.rental_id}
                title={r.rental_id}
                subtitle={`客戶: ${r.customerName} / 貨櫃: ${r.containerNo}`}
                badge={<StatusBadge status={r.status} />}
                fields={[
                  { label: '起租日期', value: r.start_date },
                  { label: '月租金', value: `$${r.monthly_rent.toLocaleString()}` }
                ]}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
