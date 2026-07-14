import { describe, expect, it } from 'vitest';
import { depositBalance, expiringRentalsWithinDays, monthlyRentCollected, occupancyRate, unpaidRent } from '../src/utils/dashboardCalculations';
import { canDeleteCustomers, canEditContainerCost, canEditContainers, canEditCustomers, canEditLedgers, canManageRentals, canManageUsers, hasPermission, profileAccessError } from '../src/utils/permissions';
const ledger = (overrides: Record<string, unknown>) => ({ ledger_id: '1', rental_id: 'r', customer_id: 'c', container_id: 'x', event_type: 'rent', amount: 100, paid_status: 'paid', period_start: '', period_end: '', due_date: '', paid_date: '2026-07-10', payment_method: '', receipt_no: '', note: '', created_at: '', updated_at: '', ...overrides });
describe('dashboard calculations', () => {
  it('calculates occupancy, collected rent, unpaid rent and deposits', () => {
    expect(occupancyRate([{ status: 'rented' }, { status: 'available' }, { status: 'retired' }] as never)).toBe(0.5);
    expect(monthlyRentCollected([ledger({})] as never, new Date('2026-07-14'))).toBe(100);
    expect(unpaidRent([ledger({ paid_status: 'unpaid', amount: 80 })] as never)).toBe(80);
    expect(depositBalance([ledger({ event_type: 'deposit_in', amount: 300 }), ledger({ event_type: 'deposit_out', amount: 90 })] as never)).toBe(210);
  });
  it('counts rentals expiring within 30 days', () => expect(expiringRentalsWithinDays([{ status: 'active', end_date: '2026-07-30' }, { status: 'active', end_date: '2026-09-01' }] as never, 30, new Date('2026-07-14'))).toBe(1));
});
describe('access controls', () => {
  it('applies role permissions', () => {
    expect(hasPermission('finance', 'ledgers:write')).toBe(true); expect(hasPermission('finance', 'containers:write')).toBe(false);
    expect(canEditCustomers('staff')).toBe(true); expect(canDeleteCustomers('staff')).toBe(false);
    expect(canEditContainers('manager')).toBe(true); expect(canEditContainerCost('staff')).toBe(false);
    expect(canManageRentals('finance')).toBe(false); expect(canEditLedgers('finance')).toBe(true); expect(canManageUsers('admin')).toBe(true);
  });
  it('rejects missing and disabled profiles', () => { expect(profileAccessError(null)).toContain('找不到'); expect(profileAccessError({ status: 'disabled' } as never)).toContain('停用'); });
});
