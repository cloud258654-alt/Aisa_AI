import { useState, useEffect } from 'react';
import { getFirebaseConfig } from '../services/firebase/firebase';
import { onSnapshot, collection } from 'firebase/firestore';
import { db } from '../services/firebase/firebase';

export default function SettingsPage() {
  const [config, setConfig] = useState({
    apiKey: '',
    authDomain: '',
    projectId: '',
    storageBucket: '',
    messagingSenderId: '',
    appId: ''
  });

  const [isSaved, setIsSaved] = useState(false);

  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isFromCache, setIsFromCache] = useState(true);
  const [hasPendingWrites, setHasPendingWrites] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState<string>('尚未同步');
  const [syncError, setSyncError] = useState<string | null>(null);

  useEffect(() => {
    // Load config values
    const currentConfig = getFirebaseConfig();
    setConfig(currentConfig);

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
        setLastSyncTime(new Date().toLocaleTimeString('zh-TW', { hour12: false }));
        setSyncError(null);
      }, (err) => {
        console.error("Settings sync status onSnapshot failed:", err);
        setSyncError(err.message);
      });
    } catch (e: any) {
      setSyncError(e.message || "讀取同步狀態出錯");
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      if (unsubscribe) unsubscribe();
    };
  }, []);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Save to localStorage
    localStorage.setItem('container_rental_firebase_api_key', config.apiKey.trim());
    localStorage.setItem('container_rental_firebase_auth_domain', config.authDomain.trim());
    localStorage.setItem('container_rental_firebase_project_id', config.projectId.trim());
    localStorage.setItem('container_rental_firebase_storage_bucket', config.storageBucket.trim());
    localStorage.setItem('container_rental_firebase_messaging_sender_id', config.messagingSenderId.trim());
    localStorage.setItem('container_rental_firebase_app_id', config.appId.trim());
    
    setIsSaved(true);
    
    // Alert the user that page reload is required to re-initialize Firebase App
    setTimeout(() => {
      if (confirm("金鑰設定已儲存！Firebase SDK 初始化需要重新載入網頁。是否現在重新整理？")) {
        window.location.reload();
      }
    }, 200);
  };

  const handleReset = () => {
    if (confirm("確定要重設金鑰嗎？這將清除您手動輸入的金鑰，並恢復使用系統預設的環境變數 ( .env )。")) {
      localStorage.removeItem('container_rental_firebase_api_key');
      localStorage.removeItem('container_rental_firebase_auth_domain');
      localStorage.removeItem('container_rental_firebase_project_id');
      localStorage.removeItem('container_rental_firebase_storage_bucket');
      localStorage.removeItem('container_rental_firebase_messaging_sender_id');
      localStorage.removeItem('container_rental_firebase_app_id');
      
      window.location.reload();
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">系統設定</h2>
        <p className="text-slate-400 mt-1">設定 Firebase Firestore 雲端金鑰，管理數據庫連線及離線機制。</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left/Center Column: Firebase Config Form */}
        <div className="glass-card rounded-2xl p-6 lg:col-span-2 space-y-6">
          <div className="flex justify-between items-center border-b border-slate-800 pb-3">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <span>🔥 Firebase SDK 憑證設定</span>
            </h3>
            <button
              onClick={handleReset}
              className="text-xs text-rose-400 hover:text-rose-300 font-semibold bg-rose-500/10 px-3 py-1.5 rounded-lg border border-rose-500/20"
            >
              重設為預設值
            </button>
          </div>

          <form onSubmit={handleSave} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">API Key</label>
                <input
                  type="text"
                  required
                  placeholder="AIzaSy..."
                  value={config.apiKey}
                  onChange={(e) => setConfig({...config, apiKey: e.target.value})}
                  className="w-full glass-input px-3 py-2.5 rounded-xl text-xs font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Auth Domain</label>
                <input
                  type="text"
                  required
                  placeholder="project-id.firebaseapp.com"
                  value={config.authDomain}
                  onChange={(e) => setConfig({...config, authDomain: e.target.value})}
                  className="w-full glass-input px-3 py-2.5 rounded-xl text-xs font-mono"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Project ID</label>
                <input
                  type="text"
                  required
                  placeholder="project-id"
                  value={config.projectId}
                  onChange={(e) => setConfig({...config, projectId: e.target.value})}
                  className="w-full glass-input px-3 py-2.5 rounded-xl text-xs font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Storage Bucket</label>
                <input
                  type="text"
                  required
                  placeholder="project-id.appspot.com"
                  value={config.storageBucket}
                  onChange={(e) => setConfig({...config, storageBucket: e.target.value})}
                  className="w-full glass-input px-3 py-2.5 rounded-xl text-xs font-mono"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Messaging Sender ID</label>
                <input
                  type="text"
                  required
                  placeholder="123456789012"
                  value={config.messagingSenderId}
                  onChange={(e) => setConfig({...config, messagingSenderId: e.target.value})}
                  className="w-full glass-input px-3 py-2.5 rounded-xl text-xs font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">App ID</label>
                <input
                  type="text"
                  required
                  placeholder="1:123456789012:web:xxxx"
                  value={config.appId}
                  onChange={(e) => setConfig({...config, appId: e.target.value})}
                  className="w-full glass-input px-3 py-2.5 rounded-xl text-xs font-mono"
                />
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 rounded-xl text-sm transition shadow shadow-indigo-650/10"
            >
              儲存 Firebase 憑證設定
            </button>
          </form>

          {isSaved && (
            <div className="p-3.5 bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400 rounded-xl">
              ✔ 憑證已更新並寫入本地儲存。重新載入頁面即可啟用新金鑰。
            </div>
          )}

          {/* Explanation on Collections */}
          <div className="border-t border-slate-850 pt-5 mt-6">
            <h4 className="text-sm font-bold text-slate-200 mb-3">📂 Firestore 雲端資料集規劃</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-400">
              <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl">
                <span className="font-bold text-indigo-400 block mb-1">customers</span>
                <span>客戶基本資料，包括姓名、電話、客戶類型、統編與停用狀態。</span>
              </div>
              <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl">
                <span className="font-bold text-indigo-400 block mb-1">containers</span>
                <span>貨櫃資產，包括規格、位置分區、成本、以及出租狀態。</span>
              </div>
              <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl">
                <span className="font-bold text-indigo-400 block mb-1">rental_records</span>
                <span>承租租約紀錄，關聯客戶與貨櫃，管理起租日、到期日與費率。</span>
              </div>
              <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl">
                <span className="font-bold text-indigo-400 block mb-1">customer_ledgers</span>
                <span>收付款財務流水，管理租金與押金收退，支援單筆登記收款。</span>
              </div>
              <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl">
                <span className="font-bold text-indigo-400 block mb-1">management_ledgers</span>
                <span>營運支出項目，如貨櫃修繕、場地地租公攤等，支援資本化標記。</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Dynamic Sync Status & Guide */}
        <div className="space-y-6 lg:col-span-1">
          {/* Sync Status Card */}
          <div className="glass-card rounded-2xl p-6 space-y-4">
            <h3 className="text-lg font-bold text-white border-b border-slate-800 pb-3 flex items-center gap-2">
              <span>📡 即時同步狀態</span>
            </h3>
            
            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center py-1.5 border-b border-slate-900">
                <span className="text-slate-400 font-semibold">網路狀態</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${isOnline ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse'}`}>
                  {isOnline ? '在線 (Online)' : '離線 (Offline)'}
                </span>
              </div>

              <div className="flex justify-between items-center py-1.5 border-b border-slate-900">
                <span className="text-slate-400 font-semibold">資料來源</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${isFromCache ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'}`}>
                  {isFromCache ? '本地快取 (Cache)' : '雲端同步 (Cloud)'}
                </span>
              </div>

              <div className="flex justify-between items-center py-1.5 border-b border-slate-900">
                <span className="text-slate-400 font-semibold">待同步寫入</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${hasPendingWrites ? 'bg-indigo-500/15 text-indigo-400 border border-indigo-500/30 animate-pulse' : 'bg-slate-800 text-slate-400'}`}>
                  {hasPendingWrites ? '⏳ 有待同步變更' : '無 (已全部同步)'}
                </span>
              </div>

              <div className="flex justify-between items-center py-1.5 border-b border-slate-900">
                <span className="text-slate-400 font-semibold">最新更新時間</span>
                <span className="text-slate-350 font-mono">{lastSyncTime}</span>
              </div>

              {syncError && (
                <div className="p-2.5 rounded bg-rose-500/10 border border-rose-500/20 text-[10px] text-rose-400 font-medium leading-normal">
                  ⚠️ 同步錯誤: {syncError}
                </div>
              )}
            </div>
          </div>

          {/* Offline Persistence Guide */}
          <div className="glass-card rounded-2xl p-6 space-y-6 text-xs leading-relaxed text-slate-400">
            <h3 className="text-lg font-bold text-white border-b border-slate-800 pb-3 font-semibold">📶 離線持久化說明</h3>
            
            <div className="space-y-3">
              <p>
                本系統已開啟 Firestore 的 **離線緩存功能 (IndexedDB Persistence)**，具備以下原生離線特性：
              </p>
              
              <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl space-y-2">
                <p className="font-semibold text-slate-200">1. 本地即時反應</p>
                <p className="text-[11px]">
                  離線時新增或修改資料，系統會即時寫入本地 IndexedDB 並向 UI 回傳更新，介面不會感到任何延遲或卡頓。
                </p>
              </div>

              <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl space-y-2">
                <p className="font-semibold text-slate-200">2. 背景自動同步</p>
                <p className="text-[11px]">
                  當網路重新連線後，且 App 處於開啟與執行狀態下，Firestore SDK 會在背景自動將本地快取變更上傳同步，無需使用者手動同步。
                </p>
              </div>

              <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl space-y-2">
                <p className="font-semibold text-slate-200">3. 跨分頁多點存取</p>
                <p className="text-[11px]">
                  支援開啟多個網頁分頁，離線資料庫會在不同分頁間自動同步，防止多點操作造成的資料衝突。
                </p>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800 text-[10px] text-slate-500 text-center">
              貨櫃營運管理系統 V1.0.0 (Firestore Edition)<br />
              Developer AI: Antigravity
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
