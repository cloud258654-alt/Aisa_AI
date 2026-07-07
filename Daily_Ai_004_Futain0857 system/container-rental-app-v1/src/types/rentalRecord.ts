// Rental record data type definition
export interface RentalRecord {
  rental_id: string; // RENT-YYYYMMDD-XXXX
  customer_id: string; // ForeignKey customers.customer_id
  container_id: string; // ForeignKey containers.container_id
  start_date: string; // YYYY-MM-DD
  end_date: string; // YYYY-MM-DD
  billing_cycle: 'monthly' | 'quarterly' | 'yearly';
  monthly_rent: number;
  deposit_amount: number;
  payment_due_day: number; // Day of month rent is due (e.g., 1, 5, 10, etc.)
  free_period_start: string; // Optional YYYY-MM-DD
  free_period_end: string; // Optional YYYY-MM-DD
  status: 'draft' | 'active' | 'ended' | 'cancelled';
  ended_date: string; // YYYY-MM-DD (when actually checked out)
  note: string;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}
