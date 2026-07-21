import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import { NAV_ITEMS } from './navConfig';
import Topbar from './Topbar';
import MobileNavDrawer from './MobileNavDrawer';
import {
  DashboardIcon,
  ContainersIcon,
  ContractsIcon,
  InvoicesIcon
} from '../ui/Icons';

export default function AppShell({ children }: { children: React.ReactNode }) {
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);
  const location = useLocation();

  const renderMobileBottomIcon = (path: string) => {
    switch (path) {
      case '/': return <DashboardIcon className="w-5 h-5" />;
      case '/containers': return <ContainersIcon className="w-5 h-5" />;
      case '/contracts': return <ContractsIcon className="w-5 h-5" />;
      case '/invoices': return <InvoicesIcon className="w-5 h-5" />;
      default: return <DashboardIcon className="w-5 h-5" />;
    }
  };

  return (
    <div className="min-h-screen bg-surface-page text-text-primary flex flex-col font-sans antialiased selection:bg-brand-gold-500/30">
      {/* Unified App Shell Layout */}
      <div className="flex flex-1 min-h-screen">
        {/* Desktop Sidebar */}
        <Sidebar />

        {/* Mobile Slide-Over Drawer */}
        <MobileNavDrawer
          isOpen={mobileDrawerOpen}
          onClose={() => setMobileDrawerOpen(false)}
        />

        {/* Main Application Container */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Top Header Bar */}
          <Topbar onToggleMobileDrawer={() => setMobileDrawerOpen(true)} />

          {/* Main Dynamic View Content */}
          <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto pb-24 sm:pb-12 animate-fade-in">
            {children}
          </main>
        </div>
      </div>

      {/* Mobile Bottom Quick Navigation Bar */}
      <div className="lg:hidden fixed bottom-0 inset-x-0 bg-brand-navy-950 border-t border-brand-navy-800 z-20 px-2 py-1.5 flex justify-around items-center shadow-2xl">
        {NAV_ITEMS.slice(0, 4).map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center py-1 px-3 rounded-lg text-[10px] font-bold transition-all ${
                isActive ? 'text-brand-gold-300' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span className="mb-0.5">{renderMobileBottomIcon(item.path)}</span>
              <span>{item.label.slice(0, 4)}</span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
