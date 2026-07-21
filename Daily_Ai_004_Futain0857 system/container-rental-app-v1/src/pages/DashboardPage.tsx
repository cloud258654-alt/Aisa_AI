import { useState, useEffect } from 'react';
import { getDashboardSummary, DashboardSummaryData } from '../services/api/dashboardApi';
import PageHeader from '../components/ui/PageHeader';
import StatCard from '../components/ui/StatCard';
import TodayTasks from '../components/dashboard/TodayTasks';
import LoadingState from '../components/ui/LoadingState';
import { TrendUpIcon, InvoicesIcon, AlertIcon, LockIcon } from '../components/ui/Icons';

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummaryData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setLoading(true);
        const summaryData = await getDashboardSummary();
        setSummary(summaryData);
      } catch (err) {
        console.error("Failed to load dashboard statistics:", err);
      } finally {
        setLoading(false);
      }
    }
    void loadDashboardData();
  }, []);

  if (loading) {
    return <LoadingState text="載入營運管理數據中..." />;
  }

  const formatCurrency = (val: number) => {
    return '$' + Math.round(val).toLocaleString();
  };

  const occupancyPercent = summary ? Math.round(summary.occupancy_rate * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Welcome & Header */}
      <PageHeader
        title="營運管理儀表板"
        description="即時掌握貨櫃出租率、今日到期與欠款風險、財務應收與保管押金。"
      />

      {/* Main Today Tasks & Risk Alerts */}
      <TodayTasks />

      {/* Main KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <StatCard
          title="總貨櫃出租率"
          value={`${occupancyPercent}%`}
          icon={<TrendUpIcon className="w-5 h-5 text-brand-navy-950" />}
          subtext={`出租中 ${summary?.rented_containers || 0} 櫃 / 營運中 ${summary ? summary.total_containers - summary.retired_containers : 0} 櫃`}
          trend={occupancyPercent >= 80 ? '高出租率' : '出租率穩定'}
          trendType={occupancyPercent >= 80 ? 'positive' : 'neutral'}
          linkTo="/containers"
        />

        <StatCard
          title="本月實收租金"
          value={formatCurrency(summary?.monthly_rent_collected || 0)}
          icon={<InvoicesIcon className="w-5 h-5 text-status-success" />}
          subtext="已入帳營運帳務"
          trend="正常入帳"
          trendType="positive"
          linkTo="/invoices"
        />

        <StatCard
          title="未收租金欠款"
          value={formatCurrency(summary?.unpaid_rent || 0)}
          icon={<AlertIcon className="w-5 h-5 text-status-danger" />}
          subtext="應收餘額催收"
          trend={(summary?.unpaid_rent || 0) > 0 ? '待催收' : '無欠款'}
          trendType={(summary?.unpaid_rent || 0) > 0 ? 'negative' : 'positive'}
          linkTo="/invoices"
        />

        <StatCard
          title="保管中押金總額"
          value={formatCurrency(summary?.deposit_balance || 0)}
          icon={<LockIcon className="w-5 h-5 text-amber-600" />}
          subtext="合約押金專戶"
          trend="安全保管"
          trendType="neutral"
          linkTo="/termination"
        />
      </div>

      {/* Secondary Details Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Container Status Breakdown */}
        <div className="saas-card p-5 space-y-4 lg:col-span-1 shadow-md">
          <h3 className="font-bold text-base text-brand-navy-950 border-b border-border-default pb-3 flex justify-between items-center">
            <span>貨櫃倉儲狀態庫存</span>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded bg-surface-muted text-text-primary border border-border-default">
              總數 {summary?.total_containers || 0} 櫃
            </span>
          </h3>

          <div className="space-y-3 text-xs sm:text-sm">
            <div className="flex justify-between items-center p-3 rounded-xl bg-surface-muted border border-border-default">
              <div className="flex items-center gap-2.5">
                <span className="w-3 h-3 rounded-full bg-status-success shadow-xs"></span>
                <span className="font-bold text-text-primary">空櫃 (AVAILABLE)</span>
              </div>
              <span className="font-extrabold text-brand-navy-950 text-base">{summary?.available_containers} 櫃</span>
            </div>

            <div className="flex justify-between items-center p-3 rounded-xl bg-surface-muted border border-border-default">
              <div className="flex items-center gap-2.5">
                <span className="w-3 h-3 rounded-full bg-status-info shadow-xs"></span>
                <span className="font-bold text-text-primary">出租中 (RENTED)</span>
              </div>
              <span className="font-extrabold text-brand-navy-950 text-base">{summary?.rented_containers} 櫃</span>
            </div>

            <div className="flex justify-between items-center p-3 rounded-xl bg-surface-muted border border-border-default">
              <div className="flex items-center gap-2.5">
                <span className="w-3 h-3 rounded-full bg-status-warning shadow-xs"></span>
                <span className="font-bold text-text-primary">維修中 (MAINTENANCE)</span>
              </div>
              <span className="font-extrabold text-brand-navy-950 text-base">{summary?.maintenance_containers} 櫃</span>
            </div>

            <div className="flex justify-between items-center p-3 rounded-xl bg-surface-muted border border-border-default text-text-secondary">
              <div className="flex items-center gap-2.5">
                <span className="w-3 h-3 rounded-full bg-gray-400"></span>
                <span className="font-semibold">已停用 (RETIRED)</span>
              </div>
              <span className="font-bold text-text-primary text-base">{summary?.retired_containers} 櫃</span>
            </div>
          </div>
        </div>

        {/* Right: Operational Expenses & Quick Actions */}
        <div className="saas-card p-5 space-y-4 lg:col-span-2 shadow-md">
          <h3 className="font-bold text-base text-brand-navy-950 border-b border-border-default pb-3">
            營運支出與快捷操作
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-surface-muted border border-border-default space-y-1">
              <span className="text-xs text-text-secondary font-bold">本月場地與營運支出</span>
              <p className="text-2xl font-extrabold text-brand-navy-950">
                {formatCurrency(summary?.monthly_expense_paid || 0)}
              </p>
              <p className="text-[11px] text-text-secondary">地租、水電及場務維修費</p>
            </div>

            <div className="p-4 rounded-xl bg-surface-muted border border-border-default space-y-1">
              <span className="text-xs text-text-secondary font-bold">生效中租賃合約</span>
              <p className="text-2xl font-extrabold text-brand-navy-950">{summary?.active_rentals || 0} 件</p>
              <p className="text-[11px] text-text-secondary">穩定長期收租客戶</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
