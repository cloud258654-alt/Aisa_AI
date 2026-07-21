import { z } from 'zod';
import { callGasApi } from './gasClient';
import { Invoice, CreateInvoiceInput } from '../../types/invoice';

export const InvoiceSchema = z.object({
  invoice_id: z.string(),
  invoice_no: z.string(),
  contract_id: z.string().optional(),
  customer_id: z.string(),
  invoice_type: z.enum(['rent', 'deposit', 'late_fee', 'cleaning_fee', 'adjustment']).catch('rent'),
  period_start: z.string().optional(),
  period_end: z.string().optional(),
  due_date: z.string(),
  amount_due: z.number(),
  amount_paid: z.number(),
  balance_due: z.number(),
  status: z.enum(['UNPAID', 'PARTIAL', 'PAID', 'VOID', 'unpaid', 'partial', 'paid', 'voided']).catch('UNPAID'),
  note: z.string().optional(),
  created_at: z.string(),
  updated_at: z.string(),
  voided_at: z.string().optional()
});

export const InvoiceListSchema = z.array(InvoiceSchema);

export async function fetchInvoices(): Promise<Invoice[]> {
  const data = await callGasApi<unknown[]>('list', { table: 'invoices' });
  return InvoiceListSchema.parse(data);
}

export async function createInvoice(input: CreateInvoiceInput): Promise<Invoice> {
  const data = await callGasApi<unknown>('create', {
    table: 'invoices',
    data: input
  });
  return InvoiceSchema.parse(data);
}

export async function updateInvoice(id: string, updates: Partial<Invoice>): Promise<Invoice> {
  const data = await callGasApi<unknown>('update', {
    table: 'invoices',
    id,
    updates
  });
  return InvoiceSchema.parse(data);
}

export async function deleteInvoice(id: string): Promise<void> {
  await callGasApi('softDelete', {
    table: 'invoices',
    id
  });
}
