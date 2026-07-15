import { ManagementLedger } from '../../types/managementLedger';
import { callGasApi } from './gasClient';

const TABLE_NAME = 'management_ledgers';

export async function listManagementLedgers(): Promise<ManagementLedger[]> {
  return callGasApi<ManagementLedger[]>('list', { table: TABLE_NAME });
}

export async function createManagementLedgerEntry(
  entryData: Omit<ManagementLedger, 'ledger_id' | 'created_at' | 'updated_at'>
): Promise<ManagementLedger> {
  return callGasApi<ManagementLedger>('create', { table: TABLE_NAME, data: entryData });
}

export async function updateManagementLedgerEntry(
  id: string,
  updates: Partial<Omit<ManagementLedger, 'ledger_id' | 'created_at'>>
): Promise<ManagementLedger> {
  return callGasApi<ManagementLedger>('update', { table: TABLE_NAME, id, updates });
}

export async function deleteManagementLedgerEntry(id: string): Promise<void> {
  await callGasApi('softDelete', { table: TABLE_NAME, id });
}
