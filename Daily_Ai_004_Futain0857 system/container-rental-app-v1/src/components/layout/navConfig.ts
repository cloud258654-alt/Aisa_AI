export interface NavItem {
  path: string;
  label: string;
  iconId: 'dashboard' | 'users' | 'containers' | 'contracts' | 'invoices' | 'termination' | 'rate-plans' | 'expenses' | 'settings';
  badge?: string | number;
}

export const NAV_ITEMS: NavItem[] = [
  { path: '/', label: '營運儀表板', iconId: 'dashboard' },
  { path: '/customers', label: '客戶管理', iconId: 'users' },
  { path: '/containers', label: '貨櫃管理', iconId: 'containers' },
  { path: '/contracts', label: '租約與合約', iconId: 'contracts' },
  { path: '/invoices', label: '應收與對帳', iconId: 'invoices' },
  { path: '/termination', label: '退租與結算', iconId: 'termination' },
  { path: '/rate-plans', label: '費率方案', iconId: 'rate-plans' },
  { path: '/management-ledgers', label: '營運支出', iconId: 'expenses' },
  { path: '/settings', label: '系統設定', iconId: 'settings' },
];
