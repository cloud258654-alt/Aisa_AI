import { useEffect, useState } from 'react';
import { useSession } from '../hooks/useSession';

export default function SettingsPage() {
  const { expiresAt, logout } = useSession();
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const online = () => setIsOnline(true);
    const offline = () => setIsOnline(false);
    window.addEventListener('online', online);
    window.addEventListener('offline', offline);
    return () => {
      window.removeEventListener('online', online);
      window.removeEventListener('offline', offline);
    };
  }, []);

  const gasWebAppUrl = import.meta.env.VITE_GAS_WEB_APP_URL || '未設定';

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-extrabold text-white">系統設定</h2>
        <p className="mt-1 text-slate-400">連線與後端狀態；後端設定僅由建置環境變數提供。</p>
      </div>
      
      <section className="glass-card max-w-2xl rounded-2xl p-6 space-y-4 text-sm">
        <h3 className="font-bold text-white text-base border-b border-slate-800 pb-2">帳號與連線狀態</h3>
        <p>登入帳號：<span className="text-indigo-300 font-semibold">系統管理員 (Admin)</span></p>
        <p>Session 到期時間：<span className="text-indigo-300 font-mono">{expiresAt ? new Date(expiresAt).toLocaleString() : '未知'}</span></p>
        <p>後端 API 網址：<span className="font-mono text-slate-300 break-all">{gasWebAppUrl}</span></p>
        <p>網路狀態：<span className={isOnline ? "text-emerald-400 font-semibold" : "text-amber-400 font-semibold"}>{isOnline ? '線上' : '離線'}</span></p>
        <p>資料庫架構：<span className="text-indigo-300">Google Drive Sheets 試算表</span></p>
        
        <button
          onClick={() => void logout()}
          className="rounded-xl border border-rose-500/20 bg-rose-500/10 px-4 py-2 text-rose-300 hover:bg-rose-500/20 transition-all font-semibold"
        >
          安全登出
        </button>
      </section>
      
      <p className="text-xs text-slate-500">
        為避免安全設定遭竄改，此頁面僅顯示基本連線與驗證中繼資料，不開放編輯試算表 ID 或密碼雜湊。
      </p>
    </div>
  );
}
