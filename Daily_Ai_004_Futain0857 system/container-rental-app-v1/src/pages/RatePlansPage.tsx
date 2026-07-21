import React, { useState, useEffect } from 'react';
import { RatePlan } from '../types/ratePlan';
import { fetchRatePlans, createRatePlan } from '../services/api/ratePlansApi';
import PageHeader from '../components/ui/PageHeader';
import DataTable from '../components/ui/DataTable';
import MobileRecordCard from '../components/ui/MobileRecordCard';
import StatusBadge from '../components/ui/StatusBadge';
import LoadingState from '../components/ui/LoadingState';
import ErrorState from '../components/ui/ErrorState';

export default function RatePlansPage() {
  const [plans, setPlans] = useState<RatePlan[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [name, setName] = useState('');
  const [containerSize, setContainerSize] = useState('20');
  const [monthlyPrice, setMonthlyPrice] = useState('4000');
  const [contractPrice, setContractPrice] = useState('48000');
  const [deposit, setDeposit] = useState('5000');

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchRatePlans();
      setPlans(data);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : '載入費率方案失敗');
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
      await createRatePlan({
        name,
        container_size_ft: Number(containerSize),
        container_type: 'standard',
        billing_cycle: 'yearly',
        contract_months: 12,
        installment_count: 1,
        first_year_discount: 0,
        standard_monthly_price: Number(monthlyPrice),
        contract_price: Number(contractPrice),
        default_deposit: Number(deposit),
        active: true
      });
      alert('費率方案新增成功！');
      setName('');
      void loadData();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : '建立失敗');
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="費率方案管理 (Rate Plans)"
        description="設定標準月租金、年合約優惠價格與預設押金金額。"
      />

      {/* New Rate Plan Form */}
      <form onSubmit={handleCreate} className="saas-card p-5 space-y-4">
        <h3 className="font-bold text-base text-brand-navy-950 border-b border-border-default pb-2">
          新增費率方案
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-5 gap-3 text-xs">
          <div>
            <label className="block font-semibold text-text-secondary mb-1">方案名稱</label>
            <input
              type="text"
              placeholder="例如 20呎年租優惠"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full saas-input"
              required
            />
          </div>
          <div>
            <label className="block font-semibold text-text-secondary mb-1">尺寸 (呎)</label>
            <input
              type="number"
              value={containerSize}
              onChange={(e) => setContainerSize(e.target.value)}
              className="w-full saas-input"
              required
            />
          </div>
          <div>
            <label className="block font-semibold text-text-secondary mb-1">月定價 ($)</label>
            <input
              type="number"
              value={monthlyPrice}
              onChange={(e) => setMonthlyPrice(e.target.value)}
              className="w-full saas-input"
              required
            />
          </div>
          <div>
            <label className="block font-semibold text-text-secondary mb-1">合約總價 ($)</label>
            <input
              type="number"
              value={contractPrice}
              onChange={(e) => setContractPrice(e.target.value)}
              className="w-full saas-input"
              required
            />
          </div>
          <div>
            <label className="block font-semibold text-text-secondary mb-1">預設押金 ($)</label>
            <input
              type="number"
              value={deposit}
              onChange={(e) => setDeposit(e.target.value)}
              className="w-full saas-input"
              required
            />
          </div>
        </div>
        <button type="submit" className="px-5 py-2 bg-brand-navy-950 text-white font-semibold text-xs rounded-lg shadow-sm">
          儲存方案
        </button>
      </form>

      {error && <ErrorState message={error} onRetry={() => void loadData()} />}

      {loading ? (
        <LoadingState text="載入費率方案中..." />
      ) : (
        <>
          <DataTable<RatePlan>
            columns={[
              {
                header: '方案名稱',
                accessor: (r) => <span className="font-bold text-brand-navy-950">{r.name}</span>
              },
              { header: '適用尺寸', accessor: (r) => `${r.container_size_ft} 呎` },
              {
                header: '月租金定價',
                accessor: (r) => <span className="font-semibold">${r.standard_monthly_price.toLocaleString()} / 月</span>
              },
              {
                header: '合約優惠總價',
                accessor: (r) => <span className="font-semibold text-brand-navy-950">${r.contract_price.toLocaleString()}</span>
              },
              {
                header: '預設押金',
                accessor: (r) => <span className="font-semibold text-amber-700">${r.default_deposit.toLocaleString()}</span>
              },
              {
                header: '狀態',
                accessor: (r) => <StatusBadge status={r.active ? 'ACTIVE' : 'INACTIVE'} />
              }
            ]}
            data={plans}
            keyExtractor={(r) => r.rate_plan_id}
            emptyText="目前尚無費率方案資料"
          />

          <div className="md:hidden space-y-3">
            {plans.map((r) => (
              <MobileRecordCard
                key={r.rate_plan_id}
                title={r.name}
                subtitle={`適用尺寸: ${r.container_size_ft} 呎`}
                badge={<StatusBadge status={r.active ? 'ACTIVE' : 'INACTIVE'} />}
                fields={[
                  { label: '月租定價', value: `$${r.standard_monthly_price.toLocaleString()}` },
                  { label: '合約優惠總價', value: `$${r.contract_price.toLocaleString()}` },
                  { label: '預設押金', value: `$${r.default_deposit.toLocaleString()}` }
                ]}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
