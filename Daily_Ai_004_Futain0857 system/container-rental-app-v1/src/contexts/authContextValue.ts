import { createContext } from 'react';
import type { User } from 'firebase/auth';
import type { UserProfile } from '../types/userProfile';

export interface AuthContextValue {
  user: User | null;
  profile: UserProfile | null;
  loading: boolean;
  error: string | null;
  logout: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);
