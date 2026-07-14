import type { UserRole } from '../types/userProfile';
import type { UserProfile } from '../types/userProfile';

export type Permission = 'customers:write' | 'customers:delete' | 'containers:write' | 'containers:cost' | 'rentals:write' | 'ledgers:write' | 'users:manage' | 'settings:read';
const permissions: Record<Permission, readonly UserRole[]> = {
  'customers:write': ['admin', 'manager', 'staff'],
  'customers:delete': ['admin', 'manager'],
  'containers:write': ['admin', 'manager'],
  'containers:cost': ['admin', 'manager'],
  'rentals:write': ['admin', 'manager'],
  'ledgers:write': ['admin', 'manager', 'finance'],
  'users:manage': ['admin'],
  'settings:read': ['admin'],
};
export function hasPermission(role: UserRole | undefined, permission: Permission): boolean {
  return role !== undefined && permissions[permission].includes(role);
}
export function canEditCustomers(role: UserRole | undefined): boolean { return hasPermission(role, 'customers:write'); }
export function canDeleteCustomers(role: UserRole | undefined): boolean { return hasPermission(role, 'customers:delete'); }
export function canEditContainers(role: UserRole | undefined): boolean { return hasPermission(role, 'containers:write'); }
export function canEditContainerCost(role: UserRole | undefined): boolean { return hasPermission(role, 'containers:cost'); }
export function canManageRentals(role: UserRole | undefined): boolean { return hasPermission(role, 'rentals:write'); }
export function canEditLedgers(role: UserRole | undefined): boolean { return hasPermission(role, 'ledgers:write'); }
export function canManageUsers(role: UserRole | undefined): boolean { return hasPermission(role, 'users:manage'); }
export function profileAccessError(profile: UserProfile | null): string | null {
  if (!profile) return '找不到使用者權限設定，請聯絡系統管理員。';
  return profile.status === 'disabled' ? '此帳號已停用，無法進入系統。' : null;
}
