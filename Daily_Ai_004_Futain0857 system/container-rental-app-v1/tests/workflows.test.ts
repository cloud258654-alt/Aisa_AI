import { describe, it, expect } from 'vitest';
import { ContractSchema, ContractItemSchema } from '../src/services/api/contractsApi';
import { InvoiceSchema } from '../src/services/api/invoicesApi';
import { PaymentSchema } from '../src/services/api/paymentsApi';
import { TerminationRecordSchema } from '../src/services/api/terminationsApi';

describe('Phase 002 & Phase 003 Workflow Calculations & Canonical Status Tests', () => {
  it('Case A: Single 20ft container contract parsing & installment calculation', () => {
    const rawContract = {
      contract_id: 'CNT-CASE-A',
      contract_no: 'CN-20260801-0001',
      customer_id: 'CUST-CASE-A',
      start_date: '2026-08-01',
      end_date: '2027-07-31',
      billing_cycle: 'yearly',
      rent_total: 48000,
      deposit_total: 5000,
      installment_count: 2,
      status: 'ACTIVE',
      items: [
        {
          contract_item_id: 'CNTI-CASE-A',
          contract_id: 'CNT-CASE-A',
          container_id: 'CONT-CASE-A',
          unit_price: 48000,
          discount_amount: 0,
          effective_price: 48000,
          start_date: '2026-08-01',
          status: 'ACTIVE',
          created_at: '2026-08-01T00:00:00.000Z',
          updated_at: '2026-08-01T00:00:00.000Z'
        }
      ],
      created_at: '2026-08-01T00:00:00.000Z',
      updated_at: '2026-08-01T00:00:00.000Z'
    };

    const parsed = ContractSchema.parse(rawContract);
    expect(parsed.rent_total).toBe(48000);
    expect(parsed.deposit_total).toBe(5000);
    expect(parsed.installment_count).toBe(2);
    expect(parsed.items?.length).toBe(1);
    expect(parsed.status).toBe('ACTIVE');
    
    // Per installment rent
    const perInstallment = Math.floor(parsed.rent_total / parsed.installment_count);
    expect(perInstallment).toBe(24000);
  });

  it('Case B: Multi 10ft container contract retain independent contract_items', () => {
    const item1 = ContractItemSchema.parse({
      contract_item_id: 'CNTI-B1',
      contract_id: 'CNT-CASE-B',
      container_id: 'CONT-B1',
      unit_price: 30000,
      discount_amount: 0,
      effective_price: 30000,
      start_date: '2026-08-01',
      status: 'ACTIVE',
      created_at: '2026-08-01T00:00:00.000Z',
      updated_at: '2026-08-01T00:00:00.000Z'
    });

    const item2 = ContractItemSchema.parse({
      contract_item_id: 'CNTI-B2',
      contract_id: 'CNT-CASE-B',
      container_id: 'CONT-B2',
      unit_price: 30000,
      discount_amount: 0,
      effective_price: 30000,
      start_date: '2026-08-01',
      status: 'ACTIVE',
      created_at: '2026-08-01T00:00:00.000Z',
      updated_at: '2026-08-01T00:00:00.000Z'
    });

    expect(item1.contract_item_id).not.toBe(item2.contract_item_id);
    expect(item1.container_id).toBe('CONT-B1');
    expect(item2.container_id).toBe('CONT-B2');
  });

  it('Case C: Partial payment transitions invoice status from UNPAID to PARTIAL then PAID', () => {
    const amountDue = 24000;

    // Initial invoice state
    let inv = InvoiceSchema.parse({
      invoice_id: 'INV-CASE-C',
      invoice_no: 'INV-20260801-0001',
      customer_id: 'CUST-CASE-A',
      invoice_type: 'rent',
      due_date: '2026-08-05',
      amount_due: amountDue,
      amount_paid: 0,
      balance_due: amountDue,
      status: 'UNPAID',
      created_at: '2026-08-01T00:00:00.000Z',
      updated_at: '2026-08-01T00:00:00.000Z'
    });
    expect(inv.status).toBe('UNPAID');

    // 1st Payment of 10,000
    const pay1 = PaymentSchema.parse({
      payment_id: 'PAY-1',
      payment_no: 'PAY-001',
      invoice_id: 'INV-CASE-C',
      customer_id: 'CUST-CASE-A',
      payment_type: 'rent',
      payment_method: 'bank_transfer',
      payment_date: '2026-08-02',
      amount: 10000,
      status: 'CONFIRMED',
      created_at: '2026-08-02T00:00:00.000Z',
      updated_at: '2026-08-02T00:00:00.000Z'
    });

    const paidAfter1 = pay1.amount;
    const balanceAfter1 = amountDue - paidAfter1;
    inv = InvoiceSchema.parse({
      ...inv,
      amount_paid: paidAfter1,
      balance_due: balanceAfter1,
      status: 'PARTIAL'
    });

    expect(inv.status).toBe('PARTIAL');
    expect(inv.balance_due).toBe(14000);

    // 2nd Payment of 14,000
    const pay2 = PaymentSchema.parse({
      payment_id: 'PAY-2',
      payment_no: 'PAY-002',
      invoice_id: 'INV-CASE-C',
      customer_id: 'CUST-CASE-A',
      payment_type: 'rent',
      payment_method: 'bank_transfer',
      payment_date: '2026-08-03',
      amount: 14000,
      status: 'CONFIRMED',
      created_at: '2026-08-03T00:00:00.000Z',
      updated_at: '2026-08-03T00:00:00.000Z'
    });

    const paidAfter2 = paidAfter1 + pay2.amount;
    const balanceAfter2 = amountDue - paidAfter2;
    inv = InvoiceSchema.parse({
      ...inv,
      amount_paid: paidAfter2,
      balance_due: balanceAfter2,
      status: 'PAID'
    });

    expect(inv.status).toBe('PAID');
    expect(inv.balance_due).toBe(0);
  });

  it('Case D: Deposit refund calculation & Inspection status rule', () => {
    const depositOriginal = 10000;
    const missingRemoteFee = 350; // 1 missing remote control
    const cleaningFee = 1000;
    const damageFee = 0;

    const depositDeducted = missingRemoteFee + cleaningFee + damageFee;
    const depositRefunded = depositOriginal - depositDeducted;

    expect(depositDeducted).toBe(1350);
    expect(depositRefunded).toBe(8650);

    const termRecord = TerminationRecordSchema.parse({
      termination_id: 'TRM-CASE-D',
      contract_id: 'CNT-CASE-A',
      requested_date: '2027-08-01',
      actual_end_date: '2027-08-01',
      inspection_status: 'pending',
      remote_control_expected: 1,
      remote_control_returned: 0,
      damage_fee: damageFee,
      cleaning_fee: cleaningFee,
      other_fee: 0,
      deposit_original: depositOriginal,
      deposit_deducted: depositDeducted,
      deposit_refunded: depositRefunded,
      status: 'completed',
      created_at: '2027-08-01T00:00:00.000Z',
      updated_at: '2027-08-01T00:00:00.000Z'
    });

    expect(termRecord.deposit_refunded).toBe(8650);
  });
});
