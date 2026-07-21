import { Link, useLocation } from 'react-router-dom';
import { useSession } from '../../hooks/useSession';
import { NAV_ITEMS } from './navConfig';
import {
  DashboardIcon,
  UsersIcon,
  ContainersIcon,
  ContractsIcon,
  InvoicesIcon,
  TerminationIcon,
  RatePlansIcon,
  ExpensesIcon,
  SettingsIcon,
  BuildingIcon,
  LogoutIcon
} from '../ui/Icons';

export default function Sidebar() {
  const { logout } = useSession();
  const location = useLocation();

  const renderIcon = (iconId: string) => {
    switch (iconId) {
      case 'dashboard': return <DashboardIcon className="w-5 h-5" />;
      case 'users': return <UsersIcon className="w-5 h-5" />;
      case 'containers': return <ContainersIcon className="w-5 h-5" />;
      case 'contracts': return <ContractsIcon className="w-5 h-5" />;
      case 'invoices': return <InvoicesIcon className="w-5 h-5" />;
      case 'termination': return <TerminationIcon className="w-5 h-5" />;
      case 'rate-plans': return <RatePlansIcon className="w-5 h-5" />;
      case 'expenses': return <ExpensesIcon className="w-5 h-5" />;
      case 'settings': return <SettingsIcon className="w-5 h-5" />;
      default: return <DashboardIcon className="w-5 h-5" />;
    }
  };

  return (
    <aside className="hidden lg:flex flex-col w-64 bg-brand-navy-950 text-white border-r border-brand-navy-800 p-5 sticky top-0 h-screen shrink-0 shadow-2xl">
      {/* Brand Logo & Header */}
      <div className="flex items-center gap-3.5 px-2 mb-8">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-gold-500 to-brand-gold-600 flex items-center justify-center text-white shadow-lg ring-1 ring-brand-gold-300/40">
          <BuildingIcon className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="font-extrabold text-base tracking-wide text-white">富田貨櫃出租</h1>
          <p className="text-[11px] text-brand-gold-300 font-semibold tracking-wider uppercase">SaaS 營運後台</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 space-y-1 overflow-y-auto pr-1">
        {NAV_ITEMS.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-semibold transition-all duration-150 ${
                isActive
                  ? 'bg-brand-navy-800 text-brand-gold-300 border-l-4 border-brand-gold-500 shadow-sm'
                  : 'text-slate-200 hover:bg-brand-navy-900 hover:text-white'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className={isActive ? 'text-brand-gold-300' : 'text-slate-300'}>
                  {renderIcon(item.iconId)}
                </span>
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && (
                <span className="px-2 py-0.5 text-[10px] rounded-full bg-brand-gold-500/20 text-brand-gold-300 font-bold border border-brand-gold-500/30">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* User Footer */}
      <div className="border-t border-brand-navy-800 pt-4 mt-auto space-y-3">
        <div className="bg-brand-navy-900 rounded-xl p-3 border border-brand-navy-800 flex items-center justify-between shadow-xs">
          <div>
            <p className="text-xs font-bold text-white">系統管理員</p>
            <p className="text-[10px] text-brand-gold-300 font-medium">Google Apps Script</p>
          </div>
          <span className="w-2.5 h-2.5 rounded-full bg-status-success shadow-sm shadow-status-success/50"></span>
        </div>

        <button
          onClick={() => void logout()}
          className="w-full py-2.5 px-3 text-xs font-bold text-rose-200 hover:text-white bg-rose-950/60 hover:bg-rose-900/80 rounded-xl border border-rose-800/40 transition-colors flex items-center justify-center gap-2 shadow-xs"
        >
          <LogoutIcon className="w-4 h-4" /> 登出系統
        </button>
      </div>
    </aside>
  );
}
