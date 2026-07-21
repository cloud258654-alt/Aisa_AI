import { useState, useEffect } from 'react';
import { fetchInvoices } from '../../services/api/invoicesApi';
import { listRentals } from '../../services/api/rentalsApi';
import { listContainers } from '../../services/api/containersApi';
import { Invoice } from '../../types/invoice';
import { RentalRecord } from '../../types/rentalRecord';
import { Container } from '../../types/container';
import { parseISO, differenceInDays } from 'date-fns';
import { Link } from 'react-router-dom';
import { AlertIcon, ContractsIcon, ContainersIcon, InvoicesIcon } from '../ui/Icons';

export default function TodayTasks() {
  const [overdueInvoices, setOverdueInvoices] = useState<Invoice[]>([]);
  const [expiringRentals, setExpiringRentals] = useState<RentalRecord[]>([]);
  const [inspectingContainersCount, setInspectingContainersCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTasksData() {
      try {
        setLoading(true);
        const [invoices, rentals, containers] = await Promise.all([
          fetchInvoices(),
          listRentals(),
          listContainers()
        ]);

        // Filter unpaid/overdue invoices
        const unpaid = invoices.filter(
          (inv: Invoice) => ((inv.status || '').toUpperCase() === 'UNPAID' || (inv.status || '').toUpperCase() === 'PARTIAL') && inv.balance_due > 0
        );
        setOverdueInvoices(unpaid);

        // Filter expiring in 30 days
        const now = new Date();
        const expiring = rentals.filter((r: RentalRecord) => {
          if ((r.status || '').toLowerCase() !== 'active' || !r.end_date) return false;
          try {
            const endDate = parseISO(r.end_date);
            const daysLeft = differenceInDays(endDate, now);
            return daysLeft >= 0 && daysLeft <= 30;
          } catch {
            return false;
          }
        });
        setExpiringRentals(expiring);

        // Inspecting containers
        const inspecting = containers.filter(
          (c: Container) => (c.status || '').toUpperCase() === 'INSPECTION'
        );
        setInspectingContainersCount(inspecting.length);
      } catch (err) {
        console.error('Failed to load today tasks:', err);
      } finally {
        setLoading(false);
      }
    }
    void loadTasksData();
  }, []);

  if (loading) {
    return (
      <div className="saas-card p-4 text-center text-xs text-text-secondary">
        讀取今日待辦與營運風險警訊中...
      </div>
    );
  }

  const totalAlerts = overdueInvoices.length + expiringRentals.length + inspectingContainersCount;

  return (
    <div className="saas-card p-5 space-y-4 border-l-4 border-brand-gold-500 shadow-md">
      <div className="flex items-center justify-between border-b border-border-default pb-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-amber-50 text-amber-700 border border-amber-200">
            <AlertIcon className="w-5 h-5 text-amber-700" />
          </div>
          <div>
            <h3 className="font-extrabold text-base text-brand-navy-950">今日營運待辦與風險警訊</h3>
            <p className="text-xs text-text-secondary">即時彙整欠款催收、到期續約與退租驗收工作</p>
          </div>
        </div>
        <span className="text-xs font-extrabold px-3 py-1 rounded-full bg-brand-navy-950 text-white shadow-xs">
          {totalAlerts} 項待處理
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Item 1: Overdue Invoices Alert */}
        <div className="p-4 rounded-xl bg-surface-muted border border-border-default space-y-2 flex flex-col justify-between">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <InvoicesIcon className="w-5 h-5 text-status-danger" />
              <span className="font-bold text-xs text-brand-navy-950">未結清應收帳款</span>
            </div>
            <span className="text-xs font-bold text-status-danger px-2 py-0.5 rounded bg-rose-50 border border-rose-200">
              {overdueInvoices.length} 筆待催收
            </span>
          </div>
          <p className="text-[11px] text-text-secondary">包含未付款與部分付款之租金帳單</p>
          <Link
            to="/invoices?status=UNPAID"
            className="text-xs font-bold text-brand-navy-950 hover:text-brand-gold-600 flex items-center justify-end gap-1 pt-1"
          >
            前往催收對帳 ➔
          </Link>
        </div>

        {/* Item 2: Expiring Contracts Alert */}
        <div className="p-4 rounded-xl bg-surface-muted border border-border-default space-y-2 flex flex-col justify-between">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <ContractsIcon className="w-5 h-5 text-amber-600" />
              <span className="font-bold text-xs text-brand-navy-950">30天內即將到期合約</span>
            </div>
            <span className="text-xs font-bold text-amber-700 px-2 py-0.5 rounded bg-amber-50 border border-amber-200">
              {expiringRentals.length} 件需續約
            </span>
          </div>
          <p className="text-[11px] text-text-secondary">聯繫客戶辦理合約續約或退租通知</p>
          <Link
            to="/contracts?status=ACTIVE"
            className="text-xs font-bold text-brand-navy-950 hover:text-brand-gold-600 flex items-center justify-end gap-1 pt-1"
          >
            查看到期合約 ➔
          </Link>
        </div>

        {/* Item 3: Inspection Containers Alert */}
        <div className="p-4 rounded-xl bg-surface-muted border border-border-default space-y-2 flex flex-col justify-between">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <ContainersIcon className="w-5 h-5 text-status-info" />
              <span className="font-bold text-xs text-brand-navy-950">退租檢驗中貨櫃</span>
            </div>
            <span className="text-xs font-bold text-status-info px-2 py-0.5 rounded bg-sky-50 border border-sky-200">
              {inspectingContainersCount} 櫃待驗收
            </span>
          </div>
          <p className="text-[11px] text-text-secondary">現場清點遙控器無誤後解鎖為空櫃</p>
          <Link
            to="/termination"
            className="text-xs font-bold text-brand-navy-950 hover:text-brand-gold-600 flex items-center justify-end gap-1 pt-1"
          >
            辦理退租驗收 ➔
          </Link>
        </div>
      </div>
    </div>
  );
}
