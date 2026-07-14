export const USER_ROLES = ['admin', 'manager', 'finance', 'staff'] as const;
export type UserRole = (typeof USER_ROLES)[number];
export type UserStatus = 'active' | 'disabled';

export interface UserProfile {
  uid: string;
  email: string;
  display_name: string;
  role: UserRole;
  status: UserStatus;
  created_at: string;
  updated_at: string;
}

export function isUserRole(value: unknown): value is UserRole {
  return typeof value === 'string' && USER_ROLES.includes(value as UserRole);
}
