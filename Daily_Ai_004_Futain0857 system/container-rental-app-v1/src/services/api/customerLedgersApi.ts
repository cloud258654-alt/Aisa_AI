import { CustomerLedger } from '../../types/customerLedger';
import { callGasApi } from './gasClient';

const TABLE_NAME = 'customer_ledgers';

export async function listCustomerLedgers(): Promise<CustomerLedger[]> {
  return callGasApi<CustomerLedger[]>('list', { table: TABLE_NAME });
}

export async function createCustomerLedgerEntry(
  entryData: Omit<CustomerLedger, 'ledger_id' | 'created_at' | 'updated_at'>
): Promise<CustomerLedger> {
  return callGasApi<CustomerLedger>('create', { table: TABLE_NAME, data: entryData });
}

export async function updateCustomerLedgerEntry(
  id: string,
  updates: Partial<Omit<CustomerLedger, 'ledger_id' | 'created_at'>>
): Promise<CustomerLedger> {
  return callGasApi<CustomerLedger>('update', { table: TABLE_NAME, id, updates });
}

export async function deleteCustomerLedgerEntry(id: string): Promise<void> {
  await callGasApi('softDelete', { table: TABLE_NAME, id });
}
