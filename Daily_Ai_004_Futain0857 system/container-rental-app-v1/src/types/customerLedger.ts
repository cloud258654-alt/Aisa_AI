// Customer Ledger data type definition (customer invoices and payments)
export interface CustomerLedger {
  ledger_id: string; // CL-YYYYMMDD-XXXX
  rental_id: string; // ForeignKey rental_records.rental_id
  customer_id: string; // ForeignKey customers.customer_id
  container_id: string; // ForeignKey containers.container_id
  event_type: 'rent' | 'deposit_in' | 'deposit_out' | 'late_fee' | 'cleaning_fee' | 'discount' | 'adjustment';
  amount: number; // positive for due/receivable, negative/positive details based on standard
  paid_status: 'paid' | 'unpaid' | 'partial' | 'cancelled';
  period_start: string; // YYYY-MM-DD (billing start date for rent)
  period_end: string; // YYYY-MM-DD (billing end date for rent)
  due_date: string; // YYYY-MM-DD (payment deadline)
  paid_date: string; // YYYY-MM-DD (actual payment date)
  payment_method: string; // e.g., 'cash', 'bank_transfer', 'line_pay'
  receipt_no: string; // Invoice/Receipt number or Drive link
  note: string;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}
