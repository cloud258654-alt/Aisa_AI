export interface Payment {
  payment_id: string;
  payment_no: string;
  invoice_id?: string;
  contract_id?: string;
  customer_id: string;
  payment_type: 'rent' | 'deposit' | 'fee';
  payment_method: 'cash' | 'bank_transfer' | 'line_pay' | 'check';
  payment_date: string;
  amount: number;
  bank_last_five?: string;
  receipt_no?: string;
  status: 'CONFIRMED' | 'VOID' | 'REFUNDED' | 'completed' | 'voided';
  note?: string;
  created_at: string;
  updated_at: string;
  voided_at?: string;
}

export type CreatePaymentInput = Omit<Payment, 'payment_id' | 'payment_no' | 'status' | 'created_at' | 'updated_at' | 'voided_at'>;
