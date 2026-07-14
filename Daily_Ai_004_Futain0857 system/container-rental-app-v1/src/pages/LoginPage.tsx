import { useState } from 'react';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../services/firebase/firebase';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password) return;

    setLoading(true);
    setError(null);

    try {
      await signInWithEmailAndPassword(auth, email.trim(), password);
    } catch (err: unknown) {
      console.error("Login failed:", err);
      const authError = err instanceof Error ? err : new Error('未知登入錯誤');
      let errMsg = "登入失敗，請檢查信箱與密碼。";
      const code = (authError as { code?: string }).code;
      if (code === 'auth/user-not-found' || code === 'auth/wrong-password' || code === 'auth/invalid-credential') {
        errMsg = "信箱或密碼輸入錯誤。";
      } else if (code === 'auth/network-request-failed') {
        errMsg = "網路連線失敗，請檢查網路連線。";
      } else if (code === 'auth/configuration-not-found') {
        errMsg = "請確認 Firebase Console 中已啟用 Email/Password 登入方式！";
      }
      setError(errMsg + ` (${code || authError.message})`);
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
          <p className="text-xs text-slate-400">請輸入登入憑證以存取系統數據</p>
        </div>

        {error && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs rounded-xl text-center leading-relaxed">
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">電子信箱 (Email)</label>
            <input
              type="email"
              required
              placeholder="admin@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full glass-input px-4 py-2.5 rounded-xl text-sm"
              disabled={loading}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">密碼 (Password)</label>
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
          <p className="font-semibold text-indigo-400">🔑 測試驗證提示：</p>
          <div className="bg-slate-900/60 p-3 border border-slate-800 rounded-xl space-y-1.5 text-left text-[11px] leading-relaxed">
            <p>1. 請至 Firebase Console ➔ Authentication ➔ <strong>Sign-in method</strong> 啟用 <strong>Email/Password</strong>。</p>
            <p>2. 在 Users 頁籤中新增一個測試帳號：</p>
            <p className="font-mono text-indigo-300 pl-2">信箱: admin@example.com</p>
            <p className="font-mono text-indigo-300 pl-2">密碼: [自訂，如 Password123]</p>
          </div>
        </div>
      </div>
    </div>
  );
}
