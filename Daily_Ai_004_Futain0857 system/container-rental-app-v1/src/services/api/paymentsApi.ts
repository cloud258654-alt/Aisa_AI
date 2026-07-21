import { z } from 'zod';
import { callGasApi } from './gasClient';
import { Payment, CreatePaymentInput } from '../../types/payment';

export const PaymentSchema = z.object({
  payment_id: z.string(),
  payment_no: z.string(),
  invoice_id: z.string().optional(),
  contract_id: z.string().optional(),
  customer_id: z.string(),
  payment_type: z.enum(['rent', 'deposit', 'fee']).catch('rent'),
  payment_method: z.enum(['cash', 'bank_transfer', 'line_pay', 'check']).catch('bank_transfer'),
  payment_date: z.string(),
  amount: z.number(),
  bank_last_five: z.string().optional(),
  receipt_no: z.string().optional(),
  status: z.enum(['CONFIRMED', 'VOID', 'REFUNDED', 'completed', 'voided']).catch('CONFIRMED'),
  note: z.string().optional(),
  created_at: z.string(),
  updated_at: z.string(),
  voided_at: z.string().optional()
});

export const PaymentListSchema = z.array(PaymentSchema);

export async function fetchPayments(): Promise<Payment[]> {
  const data = await callGasApi<unknown[]>('list', { table: 'payments' });
  return PaymentListSchema.parse(data);
}

export async function createPayment(input: CreatePaymentInput): Promise<Payment> {
  const data = await callGasApi<unknown>('recordPayment', input as unknown as Record<string, unknown>);
  return PaymentSchema.parse(data);
}

export async function voidPayment(paymentId: string, note?: string): Promise<Payment> {
  const data = await callGasApi<unknown>('voidPayment', { payment_id: paymentId, note: note || '' });
  return PaymentSchema.parse(data);
}
