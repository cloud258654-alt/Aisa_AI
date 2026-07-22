import { useState } from 'react';
import { useSession } from '../hooks/useSession';
import { BuildingIcon } from '../components/ui/Icons';

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

  const handleDemoLogin = () => {
    sessionStorage.setItem('sessionToken', 'demo_admin_token');
    sessionStorage.setItem('sessionExpiresAt', '2030-01-01T00:00:00.000Z');
    window.location.reload();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-brand-navy-950 p-4 relative overflow-hidden text-text-primary">
      {/* Background Subtle Glows */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-brand-gold-500/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-brand-navy-800/40 rounded-full blur-3xl"></div>

      <div className="w-full max-w-md bg-white rounded-2xl p-8 shadow-2xl border border-border-default relative z-10 space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-brand-gold-500 to-brand-gold-600 flex items-center justify-center text-white mx-auto shadow-md">
            <BuildingIcon className="w-7 h-7 text-white" />
          </div>
          <h2 className="text-2xl font-extrabold tracking-tight text-brand-navy-950">
            福田貨櫃倉儲出租系統
          </h2>
          <p className="text-xs text-text-secondary">請輸入管理員憑證或點選下方快捷按鈕存取系統</p>
        </div>

        {error && (
          <div className="p-3 bg-rose-50 border border-rose-200 text-status-danger text-xs rounded-xl text-center leading-relaxed font-medium">
            ⚠️ {error}
          </div>
        )}

        {/* Quick Demo Login Button - DEV / TEST ONLY */}
        {!import.meta.env.PROD && (
          <>
            <button
              type="button"
              onClick={handleDemoLogin}
              className="w-full bg-gradient-to-r from-brand-gold-500 to-brand-gold-600 hover:from-brand-gold-600 hover:to-brand-gold-600 text-white font-extrabold py-3 rounded-xl text-sm transition shadow-md flex items-center justify-center gap-2 ring-2 ring-brand-gold-300"
            >
              🚀 本機測試：點我一鍵快捷登入 (免密碼 - TEST ONLY)
            </button>

            <div className="relative flex items-center justify-center">
              <div className="border-t border-border-default w-full"></div>
              <span className="bg-white px-3 text-[11px] text-text-secondary font-medium shrink-0">或使用正式密碼登入</span>
              <div className="border-t border-border-default w-full"></div>
            </div>
          </>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1.5">管理員帳號 (Username)</label>
            <input
              type="text"
              required
              placeholder="請輸入管理員帳號"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full saas-input py-2.5"
              disabled={loading}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1.5">管理員密碼 (Password)</label>
            <input
              type="password"
              required
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full saas-input py-2.5 font-mono"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-brand-navy-950 hover:bg-brand-navy-900 text-white font-bold py-3 rounded-xl text-sm transition shadow-md disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                身分驗證中...
              </>
            ) : (
              '確認登入系統'
            )}
          </button>
        </form>

        <div className="border-t border-border-default pt-4 space-y-2 text-center text-xs text-text-secondary">
          <p className="font-semibold text-brand-gold-600">🔑 單一管理員驗證提示：</p>
          <div className="bg-surface-muted p-3 border border-border-default rounded-xl space-y-1 text-left text-[11px] leading-relaxed">
            <p>1. 請確認後端 Apps Script 的「指令碼屬性」中已設定 <strong>ADMIN_USERNAME</strong> 與對應 Hash。</p>
            <p>2. 本機開發測試可於 Console 輸入 <code>sessionStorage.setItem('sessionToken', 'demo')</code> 重整繞過。</p>
          </div>
        </div>
      </div>
    </div>
  );
}
