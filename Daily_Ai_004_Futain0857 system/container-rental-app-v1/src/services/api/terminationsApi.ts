import { z } from 'zod';
import { callGasApi } from './gasClient';
import { TerminationRecord, CreateTerminationRecordInput } from '../../types/terminationRecord';

export const TerminationRecordSchema = z.object({
  termination_id: z.string(),
  contract_id: z.string(),
  requested_date: z.string(),
  actual_end_date: z.string(),
  inspection_status: z.enum(['passed', 'failed', 'pending']).catch('passed'),
  remote_control_expected: z.number(),
  remote_control_returned: z.number(),
  damage_fee: z.number(),
  cleaning_fee: z.number(),
  other_fee: z.number(),
  deposit_original: z.number(),
  deposit_deducted: z.number(),
  deposit_refunded: z.number(),
  settlement_note: z.string().optional(),
  status: z.enum(['pending', 'completed']).catch('completed'),
  created_at: z.string(),
  updated_at: z.string()
});

export const TerminationRecordListSchema = z.array(TerminationRecordSchema);

export async function fetchTerminationRecords(): Promise<TerminationRecord[]> {
  const data = await callGasApi<unknown[]>('list', { table: 'termination_records' });
  return TerminationRecordListSchema.parse(data);
}

export async function startTermination(input: { contract_id: string }): Promise<{ contract_id: string; contract_status: string; containers_in_inspection: string[] }> {
  const data = await callGasApi<{ contract_id: string; contract_status: string; containers_in_inspection: string[] }>('startTermination', input);
  return data;
}

export async function completeTermination(input: CreateTerminationRecordInput): Promise<TerminationRecord> {
  const data = await callGasApi<unknown>('completeTermination', input as unknown as Record<string, unknown>);
  return TerminationRecordSchema.parse(data);
}

export async function completeContainerInspection(input: { container_id: string; inspection_status: 'passed' | 'failed'; note?: string }): Promise<{ container_id: string; status: string }> {
  const data = await callGasApi<{ container_id: string; status: string }>('completeContainerInspection', input);
  return data;
}
