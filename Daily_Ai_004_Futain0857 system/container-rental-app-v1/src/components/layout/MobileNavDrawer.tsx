import { Link, useLocation } from 'react-router-dom';
import { NAV_ITEMS } from './navConfig';
import { useSession } from '../../hooks/useSession';
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

interface MobileNavDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function MobileNavDrawer({ isOpen, onClose }: MobileNavDrawerProps) {
  const { logout } = useSession();
  const location = useLocation();

  if (!isOpen) return null;

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
    <div className="fixed inset-0 z-50 lg:hidden">
      {/* Backdrop */}
      <div onClick={onClose} className="fixed inset-0 bg-brand-navy-950/80 backdrop-blur-xs"></div>

      {/* Drawer */}
      <div className="fixed inset-y-0 left-0 w-72 bg-brand-navy-950 text-white shadow-2xl p-5 flex flex-col justify-between z-10 border-r border-brand-navy-800 animate-slide-in">
        <div>
          {/* Header */}
          <div className="flex items-center justify-between pb-6 mb-4 border-b border-brand-navy-800">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-gold-500 to-brand-gold-600 flex items-center justify-center text-white shadow-md">
                <BuildingIcon className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="font-bold text-sm text-white">福田貨櫃倉儲出租系統</h2>
                <p className="text-[10px] text-brand-gold-300 font-semibold">SaaS 手機選單</p>
              </div>
            </div>
            <button onClick={onClose} className="p-1.5 text-slate-300 hover:text-white rounded-lg bg-brand-navy-900">
              ✕
            </button>
          </div>

          {/* Nav List */}
          <nav className="space-y-1 overflow-y-auto max-h-[calc(100vh-200px)]">
            {NAV_ITEMS.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={onClose}
                  className={`flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-semibold transition-all ${
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
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-brand-navy-800 space-y-3">
          <button
            onClick={() => void logout()}
            className="w-full py-2.5 px-3 text-xs font-bold text-rose-200 hover:text-white bg-rose-950/60 rounded-xl border border-rose-800/40 flex items-center justify-center gap-2"
          >
            <LogoutIcon className="w-4 h-4" /> 登出系統
          </button>
        </div>
      </div>
    </div>
  );
}
