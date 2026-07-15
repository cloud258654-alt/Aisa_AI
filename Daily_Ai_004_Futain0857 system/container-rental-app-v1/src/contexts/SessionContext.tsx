import { createContext, useState, useEffect, useMemo, ReactNode } from 'react';
import { loginAdmin, logoutAdmin } from '../services/auth/authService';

export interface SessionContextValue {
  sessionToken: string | null;
  expiresAt: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

export const SessionContext = createContext<SessionContextValue | undefined>(undefined);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [sessionToken, setSessionToken] = useState<string | null>(() => sessionStorage.getItem('sessionToken'));
  const [expiresAt, setExpiresAt] = useState<string | null>(() => sessionStorage.getItem('sessionExpiresAt'));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check if session has expired locally
  const isAuthenticated = useMemo(() => {
    if (!sessionToken || !expiresAt) return false;
    const expiresTime = new Date(expiresAt).getTime();
    return new Date().getTime() < expiresTime;
  }, [sessionToken, expiresAt]);

  const login = async (username: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await loginAdmin(username, password);
      sessionStorage.setItem('sessionToken', res.sessionToken);
      sessionStorage.setItem('sessionExpiresAt', res.expiresAt);
      setSessionToken(res.sessionToken);
      setExpiresAt(res.expiresAt);
    } catch (err: any) {
      const errMsg = err.message || '登入失敗，請確認帳號或密碼。';
      setError(errMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      if (sessionToken) {
        await logoutAdmin(sessionToken);
      }
    } finally {
      sessionStorage.removeItem('sessionToken');
      sessionStorage.removeItem('sessionExpiresAt');
      setSessionToken(null);
      setExpiresAt(null);
      setError(null);
      setLoading(false);
    }
  };

  // Listen to session expiry event dispatched by gasClient
  useEffect(() => {
    const handleExpiry = () => {
      setSessionToken(null);
      setExpiresAt(null);
      setError('登入逾期或未授權，已自動登出。');
    };
    
    window.addEventListener('session-expired', handleExpiry);
    return () => {
      window.removeEventListener('session-expired', handleExpiry);
    };
  }, []);

  const value = useMemo(() => ({
    sessionToken,
    expiresAt,
    isAuthenticated,
    loading,
    error,
    login,
    logout
  }), [sessionToken, expiresAt, isAuthenticated, loading, error]);

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}
