import { isSameMonth, parseISO } from 'date-fns';
import type { Container } from '../types/container';
import type { CustomerLedger } from '../types/customerLedger';
import type { RentalRecord } from '../types/rentalRecord';

export function occupancyRate(containers: Container[]): number {
  const active = containers.filter((item) => !item.deleted_at && item.status !== 'retired');
  return active.length === 0 ? 0 : active.filter((item) => item.status === 'rented').length / active.length;
}
export function monthlyRentCollected(entries: CustomerLedger[], now = new Date()): number {
  return entries.filter((item) => !item.deleted_at && item.event_type === 'rent' && item.paid_status === 'paid' && item.paid_date && isSameMonth(parseISO(item.paid_date), now)).reduce((sum, item) => sum + Number(item.amount || 0), 0);
}
export function unpaidRent(entries: CustomerLedger[]): number { return entries.filter((item) => !item.deleted_at && item.event_type === 'rent' && (item.paid_status === 'unpaid' || item.paid_status === 'partial')).reduce((sum, item) => sum + Number(item.amount || 0), 0); }
export function depositBalance(entries: CustomerLedger[]): number { return entries.filter((item) => !item.deleted_at && item.paid_status === 'paid').reduce((sum, item) => sum + (item.event_type === 'deposit_in' ? Number(item.amount) : item.event_type === 'deposit_out' ? -Number(item.amount) : 0), 0); }
export function expiringRentalsWithinDays(rentals: RentalRecord[], days: number, now = new Date()): number {
  const end = new Date(now); end.setDate(end.getDate() + days);
  return rentals.filter((item) => !item.deleted_at && item.status === 'active' && item.end_date && parseISO(item.end_date) >= now && parseISO(item.end_date) <= end).length;
}
