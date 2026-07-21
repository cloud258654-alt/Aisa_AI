export interface Invoice {
  invoice_id: string;
  invoice_no: string;
  contract_id?: string;
  customer_id: string;
  invoice_type: 'rent' | 'deposit' | 'late_fee' | 'cleaning_fee' | 'adjustment';
  period_start?: string;
  period_end?: string;
  due_date: string;
  amount_due: number;
  amount_paid: number;
  balance_due: number;
  status: 'UNPAID' | 'PARTIAL' | 'PAID' | 'VOID' | 'unpaid' | 'partial' | 'paid' | 'voided';
  note?: string;
  created_at: string;
  updated_at: string;
  voided_at?: string;
}

export type CreateInvoiceInput = Omit<Invoice, 'invoice_id' | 'invoice_no' | 'amount_paid' | 'balance_due' | 'status' | 'created_at' | 'updated_at' | 'voided_at'>;
