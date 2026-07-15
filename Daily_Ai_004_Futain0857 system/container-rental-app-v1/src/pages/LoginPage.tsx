import { useState } from 'react';
import { useSession } from '../hooks/useSession';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const { login } = useSession();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password) return;

    setLoading(true);
    setError(null);

    try {
      await login(username.trim(), password);
    } catch (err: unknown) {
      console.error("Login failed:", err);
      setError(err instanceof Error ? err.message : '登入失敗，請檢查管理員帳號與密碼。');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 p-4 relative overflow-hidden">
      {/* Dynamic Background Glows */}
      <div className="absolute top-1/4 left-1/4 w-80 h-80 bg-indigo-600/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-purple-600/10 rounded-full blur-3xl animate-pulse delay-1000"></div>

      <div className="w-full max-w-md glass-panel p-8 rounded-2xl border border-slate-800 shadow-2xl relative z-10 space-y-6">
        <div className="text-center space-y-2">
          <span className="text-4xl inline-block animate-bounce">🏗️</span>
          <h2 className="text-2xl font-extrabold tracking-wider bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            貨櫃出租 V1 登入
          </h2>
          <p className="text-xs text-slate-400">請輸入管理員憑證以存取系統數據</p>
        </div>

        {error && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs rounded-xl text-center leading-relaxed">
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">管理員帳號 (Username)</label>
            <input
              type="text"
              required
              placeholder="請輸入管理員帳號"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full glass-input px-4 py-2.5 rounded-xl text-sm"
              disabled={loading}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">管理員密碼 (Password)</label>
            <input
              type="password"
              required
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full glass-input px-4 py-2.5 rounded-xl text-sm font-mono"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold py-3 rounded-xl text-sm transition shadow-lg shadow-indigo-650/15 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                登入中...
              </>
            ) : (
              '確認登入'
            )}
          </button>
        </form>

        <div className="border-t border-slate-850 pt-4 space-y-2 text-center text-xs text-slate-400">
          <p className="font-semibold text-indigo-400">🔑 系統驗證提示：</p>
          <div className="bg-slate-900/60 p-3 border border-slate-800 rounded-xl space-y-1.5 text-left text-[11px] leading-relaxed">
            <p>1. 請確認後端 Google Apps Script 的「指令碼屬性」中已設定 <strong>ADMIN_USERNAME</strong> 與對應的密碼雜湊。</p>
            <p>2. 請確認前端已於環境變數配置正確的 <strong>VITE_GAS_WEB_APP_URL</strong> 網址並重新發布。</p>
          </div>
        </div>
      </div>
    </div>
  );
}
