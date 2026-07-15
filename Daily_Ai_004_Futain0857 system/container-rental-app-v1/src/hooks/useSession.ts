import { useContext } from 'react';
import { SessionContext } from '../contexts/SessionContext';

export function useSession() {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession 必須在 SessionProvider 內使用。');
  }
  return context;
}
