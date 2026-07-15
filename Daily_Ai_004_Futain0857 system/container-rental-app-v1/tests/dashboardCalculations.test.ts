import { describe, expect, it } from 'vitest';
import { occupancyRate, monthlyRentCollected, unpaidRent, depositBalance, expiringRentalsWithinDays } from '../src/utils/dashboardCalculations';
import { CustomerLedger } from '../src/types/customerLedger';
import { RentalRecord } from '../src/types/rentalRecord';
import { Container } from '../src/types/container';

const mockLedger = (overrides: Partial<CustomerLedger>): CustomerLedger => ({
  ledger_id: '1',
  rental_id: 'r1',
  customer_id: 'c1',
  container_id: 'x1',
  event_type: 'rent',
  amount: 100,
  paid_status: 'paid',
  period_start: '',
  period_end: '',
  due_date: '',
  paid_date: '2026-07-10',
  payment_method: '',
  receipt_no: '',
  note: '',
  created_at: '',
  updated_at: '',
  ...overrides
});

describe('dashboard calculations', () => {
  it('calculates occupancy, collected rent, unpaid rent and deposits', () => {
    const containers: Partial<Container>[] = [
      { status: 'rented' },
      { status: 'available' },
      { status: 'retired' }
    ];
    expect(occupancyRate(containers as Container[])).toBe(0.5);

    const ledgers: CustomerLedger[] = [
      mockLedger({ amount: 100, paid_status: 'paid', paid_date: '2026-07-10' })
    ];
    expect(monthlyRentCollected(ledgers, new Date('2026-07-14'))).toBe(100);

    const unpaid: CustomerLedger[] = [
      mockLedger({ paid_status: 'unpaid', amount: 80 })
    ];
    expect(unpaidRent(unpaid)).toBe(80);

    const deposits: CustomerLedger[] = [
      mockLedger({ event_type: 'deposit_in', paid_status: 'paid', amount: 300 }),
      mockLedger({ event_type: 'deposit_out', paid_status: 'paid', amount: 90 })
    ];
    expect(depositBalance(deposits)).toBe(210);
  });

  it('counts rentals expiring within 30 days', () => {
    const rentals: Partial<RentalRecord>[] = [
      { status: 'active', end_date: '2026-07-30' },
      { status: 'active', end_date: '2026-09-01' }
    ];
    expect(expiringRentalsWithinDays(rentals as RentalRecord[], 30, new Date('2026-07-14'))).toBe(1);
  });
});
