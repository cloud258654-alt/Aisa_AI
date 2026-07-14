import type { ReactNode } from 'react';
import { hasPermission, type Permission } from '../../utils/permissions';
import { useAuth } from '../../hooks/useAuth';
export default function PermissionGuard({ permission, children }: { permission: Permission; children: ReactNode }) {
  const { profile } = useAuth();
  if (!hasPermission(profile?.role, permission)) return <div className="p-6 text-rose-400">您沒有操作此功能的權限。</div>;
  return <>{children}</>;
}
