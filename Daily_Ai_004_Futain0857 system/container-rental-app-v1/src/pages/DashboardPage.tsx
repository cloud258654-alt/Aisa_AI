import { useState, useEffect } from 'react';
import { getDashboardSummary, DashboardSummaryData } from '../services/api/dashboardApi';
import { listRentals } from '../services/api/rentalsApi';
import { listCustomers } from '../services/api/customersApi';
import { listContainers } from '../services/api/containersApi';
import { RentalRecord } from '../types/rentalRecord';
import { parseISO } from 'date-fns';
import { Link } from 'react-router-dom';

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [expiringContracts, setExpiringContracts] = useState<Array<RentalRecord & { customerName?: string; containerNo?: string }>>([]);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setLoading(true);
        // Load summary
        const summaryData = await getDashboardSummary();
        setSummary(summaryData);

        // Load details for expiring rentals list
        const [rentals, customers, containers] = await Promise.all([
          listRentals(),
          listCustomers(),
          listContainers()
        ]);

        // Filter expiring in 30 days
        const now = new Date();
        const thirtyDaysLater = new Date();
        thirtyDaysLater.setDate(now.getDate() + 30);

        const expiringList = rentals
          .filter(r => {
            if (r.status !== 'active' || !r.end_date) return false;
            try {
              const d = parseISO(r.end_date);
              return d >= now && d <= thirtyDaysLater;
            } catch (e) {
              return false;
            }
          })
          .map(r => {
            const cust = customers.find(c => c.customer_id === r.customer_id);
            const cont = containers.find(c => c.container_id === r.container_id);
            return {
              ...r,
              customerName: cust ? cust.name : '未知客戶',
              containerNo: cont ? cont.container_no : '未知編號'
            };
          });

        setExpiringContracts(expiringList);
      } catch (err) {
        console.error("Failed to load dashboard statistics:", err);
      } finally {
        setLoading(false);
      }
    }

    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-400 font-medium">載入營運數據中...</p>
      </div>
    );
  }

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD', maximumFractionDigits: 0 }).format(val);
  };

  const occupancyPercent = summary ? Math.round(summary.occupancy_rate * 100) : 0;

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">營運管理看板</h2>
        <p className="text-slate-400 mt-1">即時掌握貨櫃出租率、客戶帳務及營運支出狀態。</p>
      </div>

      {/* Main KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        
        {/* KPI 1: Occupancy Rate */}
        <div className="glass-card rounded-2xl p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/10 rounded-full blur-xl -mr-6 -mt-6"></div>
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-semibold text-slate-400">總出租率</p>
              <h3 className="text-3xl font-bold text-white mt-2">{occupancyPercent}%</h3>
            </div>
            <span className="text-2xl bg-indigo-500/10 p-3 rounded-xl">📈</span>
          </div>
          {/* Progress bar */}
          <div className="w-full bg-slate-800 h-2 rounded-full mt-4 overflow-hidden">
            <div className="bg-indigo-500 h-full rounded-full transition-all duration-500" style={{ width: `${occupancyPercent}%` }}></div>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            出租中: {summary?.rented_containers} 櫃 / 營運中: {summary ? (summary.total_containers - summary.retired_containers) : 0} 櫃
          </p>
        </div>

        {/* KPI 2: Revenue Collected */}
        <div className="glass-card rounded-2xl p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-full blur-xl -mr-6 -mt-6"></div>
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-semibold text-slate-400">本月已收租金</p>
              <h3 className="text-3xl font-bold text-emerald-400 mt-2">
                {formatCurrency(summary?.monthly_rent_collected || 0)}
              </h3>
            </div>
            <span className="text-2xl bg-emerald-500/10 p-3 rounded-xl">💰</span>
          </div>
          <div className="flex items-center gap-1.5 mt-5">
            <span className="text-emerald-500 text-xs font-semibold">✔</span>
            <p className="text-xs text-slate-400">已入帳營運流水</p>
          </div>
        </div>

        {/* KPI 3: Unpaid Revenue */}
        <div className="glass-card rounded-2xl p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-rose-500/10 rounded-full blur-xl -mr-6 -mt-6"></div>
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-semibold text-slate-400">未收租金欠款</p>
              <h3 className="text-3xl font-bold text-rose-400 mt-2">
                {formatCurrency(summary?.unpaid_rent || 0)}
              </h3>
            </div>
            <span className="text-2xl bg-rose-500/10 p-3 rounded-xl">⚠️</span>
          </div>
          <div className="flex items-center gap-1.5 mt-5">
            <span className="text-rose-500 text-xs font-semibold">●</span>
            <p className="text-xs text-slate-400">待催收應收帳款</p>
          </div>
        </div>

        {/* KPI 4: Monthly Expense */}
        <div className="glass-card rounded-2xl p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/10 rounded-full blur-xl -mr-6 -mt-6"></div>
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-semibold text-slate-400">本月營運支出</p>
              <h3 className="text-3xl font-bold text-purple-400 mt-2">
                {formatCurrency(summary?.monthly_expense_paid || 0)}
              </h3>
            </div>
            <span className="text-2xl bg-purple-500/10 p-3 rounded-xl">🛠️</span>
          </div>
          <div className="flex items-center gap-1.5 mt-5">
            <span className="text-purple-500 text-xs font-semibold">●</span>
            <p className="text-xs text-slate-400">地租、維修及水電雜支</p>
          </div>
        </div>

      </div>

      {/* Secondary metrics grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Card: Container Inventory Summary */}
        <div className="glass-card rounded-2xl p-6 lg:col-span-1 space-y-6">
          <h4 className="text-lg font-bold text-white border-b border-slate-800 pb-3 flex items-center justify-between">
            <span>貨櫃倉儲庫存</span>
            <span className="text-xs text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded-full font-semibold">
              總數: {summary?.total_containers} 櫃
            </span>
          </h4>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center text-sm p-3 rounded-xl bg-slate-900/60 border border-slate-800/40">
              <div className="flex items-center gap-3">
                <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
                <span>空櫃 (Available)</span>
              </div>
              <span className="font-bold text-white text-base">{summary?.available_containers} 櫃</span>
            </div>

            <div className="flex justify-between items-center text-sm p-3 rounded-xl bg-slate-900/60 border border-slate-800/40">
              <div className="flex items-center gap-3">
                <span className="w-3 h-3 rounded-full bg-indigo-500"></span>
                <span>出租中 (Rented)</span>
              </div>
              <span className="font-bold text-white text-base">{summary?.rented_containers} 櫃</span>
            </div>

            <div className="flex justify-between items-center text-sm p-3 rounded-xl bg-slate-900/60 border border-slate-800/40">
              <div className="flex items-center gap-3">
                <span className="w-3 h-3 rounded-full bg-amber-500"></span>
                <span>維修中 (Maintenance)</span>
              </div>
              <span className="font-bold text-white text-base">{summary?.maintenance_containers} 櫃</span>
            </div>

            <div className="flex justify-between items-center text-sm p-3 rounded-xl bg-slate-900/60 border border-slate-800/40 text-slate-400">
              <div className="flex items-center gap-3">
                <span className="w-3 h-3 rounded-full bg-slate-600"></span>
                <span>已停用 (Retired)</span>
              </div>
              <span className="font-bold text-slate-200 text-base">{summary?.retired_containers} 櫃</span>
            </div>
          </div>

          <div className="pt-2 text-center">
            <Link to="/containers" className="text-indigo-400 text-xs font-semibold hover:text-indigo-300">
              管理貨櫃狀態 →
            </Link>
          </div>
        </div>

        {/* Center / Right Card: Financial Balances & Expiring Rentals */}
        <div className="glass-card rounded-2xl p-6 lg:col-span-2 space-y-6">
          <h4 className="text-lg font-bold text-white border-b border-slate-800 pb-3 flex justify-between items-center">
            <span>租約與押金概況</span>
            <span className="text-xs text-slate-400">當前統計</span>
          </h4>

          {/* Quick Balance Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-900/30 flex items-center justify-between">
              <div>
                <p className="text-xs text-indigo-300 font-medium">租賃合約生效中</p>
                <p className="text-2xl font-bold text-white mt-1">{summary?.active_rentals} 件</p>
              </div>
              <span className="text-2xl">📝</span>
            </div>
            
            <div className="p-4 rounded-xl bg-purple-950/20 border border-purple-900/30 flex items-center justify-between">
              <div>
                <p className="text-xs text-purple-300 font-medium">保管中押金餘額</p>
                <p className="text-2xl font-bold text-white mt-1">{formatCurrency(summary?.deposit_balance || 0)}</p>
              </div>
              <span className="text-2xl">🔐</span>
            </div>
          </div>

          {/* 30-Day Expiring Contracts List */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <h5 className="text-sm font-semibold text-slate-300">⚠️ 30 天內即將到期合約 ({summary?.expiring_rentals_30_days || 0})</h5>
              {expiringContracts.length > 0 && (
                <span className="text-[10px] text-amber-500 font-bold px-2 py-0.5 rounded-full bg-amber-500/10">
                  需要續約處理
                </span>
              )}
            </div>

            {expiringContracts.length === 0 ? (
              <div className="text-center py-6 text-slate-500 text-xs border border-dashed border-slate-800 rounded-xl">
                目前無即將到期的租約。
              </div>
            ) : (
              <div className="overflow-x-auto max-h-48 overflow-y-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-900 text-slate-400 uppercase text-[10px]">
                    <tr>
                      <th className="px-4 py-2">貨櫃編號</th>
                      <th className="px-4 py-2">客戶</th>
                      <th className="px-4 py-2">月租金</th>
                      <th className="px-4 py-2 text-right">到期日</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50">
                    {expiringContracts.map((r) => (
                      <tr key={r.rental_id} className="hover:bg-slate-900/40">
                        <td className="px-4 py-3 font-semibold text-indigo-400">{r.containerNo}</td>
                        <td className="px-4 py-3">{r.customerName}</td>
                        <td className="px-4 py-3">{formatCurrency(r.monthly_rent)}</td>
                        <td className="px-4 py-3 text-right text-amber-400 font-medium">{r.end_date}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

        </div>

      </div>
    </div>
  );
}
