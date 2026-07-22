import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { NAV_ITEMS } from './navConfig';
import { SearchIcon, BuildingIcon } from '../ui/Icons';

interface TopbarProps {
  onToggleMobileDrawer: () => void;
}

export default function Topbar({ onToggleMobileDrawer }: TopbarProps) {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const location = useLocation();

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const currentNav = NAV_ITEMS.find((n) => n.path === location.pathname);

  return (
    <header className="bg-brand-navy-950 text-white border-b border-brand-navy-800 sticky top-0 z-30 px-4 sm:px-6 py-3 shadow-lg">
      <div className="flex items-center justify-between gap-4">
        {/* Left: Mobile Menu Toggle & Title Breadcrumb */}
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleMobileDrawer}
            className="lg:hidden p-2 text-slate-200 hover:text-white hover:bg-brand-navy-800 rounded-lg transition-colors"
            aria-label="Toggle Navigation Drawer"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          {/* Mobile Brand Logo */}
          <div className="lg:hidden flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-brand-gold-500 flex items-center justify-center text-white">
              <BuildingIcon className="w-5 h-5 text-white" />
            </div>
            <span className="font-extrabold text-sm text-white">福田貨櫃</span>
          </div>

          {/* Breadcrumb Title */}
          <div className="hidden sm:flex items-center gap-2 text-xs font-semibold text-slate-300">
            <span className="text-slate-400">控制台</span>
            <span className="text-brand-gold-500">/</span>
            <span className="text-white font-bold text-sm sm:text-base">
              {currentNav?.label || '頁面管理'}
            </span>
          </div>
        </div>

        {/* Center: Search Input */}
        <div className="flex-1 max-w-xs sm:max-w-md mx-2">
          <div className="relative">
            <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
              <SearchIcon className="w-4 h-4" />
            </span>
            <input
              type="text"
              placeholder="全站快速搜尋 (櫃號 / 客戶 / 合約)..."
              className="w-full pl-9 pr-4 py-1.5 bg-brand-navy-900/80 border border-brand-navy-800 rounded-lg text-xs text-white placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-brand-gold-500/50 transition-all"
            />
          </div>
        </div>

        {/* Right: Status Indicator & User Info */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-brand-navy-900 border border-brand-navy-800 text-[11px] font-semibold text-slate-200">
            <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-status-success animate-pulse' : 'bg-status-danger'}`}></span>
            <span className="hidden md:inline">{isOnline ? '系統連線正常' : '網路中斷 (離線)'}</span>
          </div>

          <div className="hidden sm:flex items-center gap-2 pl-2 border-l border-brand-navy-800 text-xs">
            <span className="w-7 h-7 rounded-full bg-brand-gold-500/20 text-brand-gold-300 font-bold border border-brand-gold-500/30 flex items-center justify-center text-xs">
              首
            </span>
            <span className="font-bold text-white text-xs">管理員</span>
          </div>
        </div>
      </div>
    </header>
  );
}
