import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { onSnapshot, collection } from 'firebase/firestore';
import { signOut } from 'firebase/auth';
import { db, auth } from '../../services/firebase/firebase';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isFromCache, setIsFromCache] = useState(true);
  const [hasPendingWrites, setHasPendingWrites] = useState(false);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Subscribe to containers metadata to watch offline status dynamically
    let unsubscribe: (() => void) | undefined;
    try {
      unsubscribe = onSnapshot(collection(db, 'containers'), (snapshot) => {
        setIsFromCache(snapshot.metadata.fromCache);
        setHasPendingWrites(snapshot.metadata.hasPendingWrites);
      }, (err) => {
        console.error("Layout firestore onSnapshot failed:", err);
      });
    } catch (e) {
      console.error(e);
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      if (unsubscribe) unsubscribe();
    };
  }, []);

  const navItems = [
    { path: '/', label: '儀表板', icon: '📊' },
    { path: '/customers', label: '客戶管理', icon: '👥' },
    { path: '/containers', label: '貨櫃管理', icon: '📦' },
    { path: '/rentals', label: '租約管理', icon: '📜' },
    { path: '/customer-ledgers', label: '客戶帳務', icon: '💰' },
    { path: '/management-ledgers', label: '場地支出', icon: '🛠️' },
    { path: '/settings', label: '系統設定', icon: '⚙️' },
  ];

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-slate-950 text-slate-100">
      
      {/* Sidebar for Desktop */}
      <aside className="hidden lg:flex flex-col w-64 glass-panel border-r border-slate-800 p-6 sticky top-0 h-screen shrink-0">
        <div className="flex items-center gap-3 mb-8">
          <span className="text-3xl">🏗️</span>
          <div>
            <h1 className="font-bold text-lg tracking-wider bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
              貨櫃出租 V1
            </h1>
            <p className="text-xs text-slate-400">智能營運管理系統</p>
          </div>
        </div>

        {/* Navigation links */}
        <nav className="flex-1 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-indigo-600/80 to-purple-600/80 text-white font-medium shadow-md shadow-indigo-600/10'
                    : 'text-slate-400 hover:bg-slate-800/40 hover:text-slate-200'
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Footer in Sidebar */}
        <div className="border-t border-slate-800 pt-4 mt-auto space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">連線狀態</span>
            <div className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-500 shadow-emerald-500/50 shadow' : 'bg-amber-500 shadow-amber-500/50 shadow animate-pulse'}`}></span>
              <span className="font-medium text-slate-300">{isOnline ? '線上' : '離線暫存'}</span>
            </div>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">資料來源</span>
            <span className="text-slate-300 font-medium">{isFromCache ? '本地快取' : '雲端同步'}</span>
          </div>
          {hasPendingWrites && (
            <div className="p-2 rounded bg-indigo-950/40 border border-indigo-900/60 text-[10px] text-indigo-300 text-center animate-pulse">
              ⏳ 有待同步變更
            </div>
          )}
          <button
            onClick={() => signOut(auth)}
            className="w-full mt-2 text-xs text-rose-400 hover:text-rose-300 font-semibold bg-rose-500/10 hover:bg-rose-500/20 py-2 rounded-xl border border-rose-500/20 transition-all duration-200"
          >
            🚪 帳號登出
          </button>
        </div>
      </aside>

      {/* Mobile Top Header */}
      <header className="lg:hidden glass-panel border-b border-slate-800 px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🏗️</span>
          <div>
            <h1 className="font-bold text-base tracking-wider bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
              貨櫃出租 V1
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => signOut(auth)}
            className="p-1.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-450 border border-rose-500/20 text-xs flex items-center justify-center font-bold"
            title="登出"
          >
            🚪
          </button>
          {hasPendingWrites && (
            <span className="text-[10px] bg-indigo-950 border border-indigo-850 text-indigo-300 px-2 py-0.5 rounded-full font-semibold animate-pulse">
              ⏳ 待同步
            </span>
          )}
          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 px-3 py-1 rounded-full text-xs">
            <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-500' : 'bg-amber-500 animate-pulse'}`}></span>
            <span>{isOnline ? (isFromCache ? '快取' : '同步') : '離線'}</span>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 overflow-x-hidden overflow-y-auto p-4 md:p-8 lg:p-10 pb-24 lg:pb-10 min-h-screen">
        <div className="max-w-7xl mx-auto animate-slide-up">
          {children}
        </div>
      </main>

      {/* Mobile Bottom Navigation Bar */}
      <nav className="lg:hidden fixed bottom-0 left-0 right-0 glass-panel border-t border-slate-800 px-2 py-2 flex justify-around items-center z-50">
        {navItems.slice(0, 6).map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center py-1.5 px-3 rounded-lg transition-all ${
                isActive ? 'text-indigo-400 font-semibold' : 'text-slate-400'
              }`}
            >
              <span className="text-xl mb-0.5">{item.icon}</span>
              <span className="text-[10px] tracking-wide">{item.label.replace('管理', '')}</span>
            </Link>
          );
        })}
        <Link
          to="/settings"
          className={`flex flex-col items-center py-1.5 px-3 rounded-lg transition-all ${
            location.pathname === '/settings' ? 'text-indigo-400 font-semibold' : 'text-slate-400'
          }`}
        >
          <span className="text-xl mb-0.5">⚙️</span>
          <span className="text-[10px] tracking-wide">設定</span>
        </Link>
      </nav>
    </div>
  );
}
