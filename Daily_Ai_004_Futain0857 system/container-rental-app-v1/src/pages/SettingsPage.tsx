import { collection, onSnapshot } from 'firebase/firestore';
import { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { db, getFirebaseConfig } from '../services/firebase/firebase';

export default function SettingsPage() {
  const { user, profile, logout } = useAuth();
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [fromCache, setFromCache] = useState(true);
  const [pending, setPending] = useState(false);
  useEffect(() => {
    const online = () => setIsOnline(true); const offline = () => setIsOnline(false);
    window.addEventListener('online', online); window.addEventListener('offline', offline);
    const unsubscribe = onSnapshot(collection(db, 'containers'), snapshot => { setFromCache(snapshot.metadata.fromCache); setPending(snapshot.metadata.hasPendingWrites); });
    return () => { window.removeEventListener('online', online); window.removeEventListener('offline', offline); unsubscribe(); };
  }, []);
  const projectId = getFirebaseConfig().projectId || '未設定';
  return <div className="space-y-6"><div><h2 className="text-3xl font-extrabold text-white">系統設定</h2><p className="mt-1 text-slate-400">連線與帳號資訊；Firebase 設定僅由建置環境變數提供。</p></div>
    <section className="glass-card max-w-2xl rounded-2xl p-6 space-y-3 text-sm"><h3 className="font-bold text-white">帳號與連線狀態</h3>
      <p>登入帳號：<span className="text-indigo-300">{user?.email ?? '未知'}</span></p><p>角色：<span className="text-indigo-300">{profile?.role ?? '未知'}</span></p><p>Firebase Project ID：<span className="font-mono text-slate-300">{projectId}</span></p>
      <p>網路：{isOnline ? '線上' : '離線'}</p><p>Firestore：{fromCache ? '本地快取' : '雲端同步'}{pending ? '（有待同步寫入）' : ''}</p>
      <button onClick={() => void logout()} className="rounded-xl border border-rose-500/20 bg-rose-500/10 px-4 py-2 text-rose-300">登出</button>
    </section><p className="text-xs text-slate-500">為避免設定遭竄改，頁面不顯示或編輯 API Key、App ID 等 Firebase 設定。</p></div>;
}
