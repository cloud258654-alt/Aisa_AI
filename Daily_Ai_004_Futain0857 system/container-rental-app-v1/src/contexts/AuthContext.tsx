import { onAuthStateChanged, signOut, type User } from 'firebase/auth';
import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { auth } from '../services/firebase/firebase';
import { getUserProfile } from '../services/auth/userProfileService';
import { profileAccessError } from '../utils/permissions';
import { AuthContext, type AuthContextValue } from './authContextValue';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => onAuthStateChanged(auth, async (nextUser) => {
    setUser(nextUser); setProfile(null); setError(null);
    if (!nextUser) { setLoading(false); return; }
    try {
      const nextProfile = await getUserProfile(nextUser.uid);
      const accessError = profileAccessError(nextProfile);
      if (accessError) throw new Error(accessError);
      setProfile(nextProfile);
    } catch (reason) { setError(reason instanceof Error ? reason.message : '無法載入使用者權限。'); }
    finally { setLoading(false); }
  }), []);
  const value = useMemo(() => ({ user, profile, loading, error, logout: () => signOut(auth) }), [user, profile, loading, error]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
