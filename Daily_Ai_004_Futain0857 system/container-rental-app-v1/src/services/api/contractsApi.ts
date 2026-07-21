import { z } from 'zod';
import { callGasApi } from './gasClient';
import { Contract, CreateContractInput } from '../../types/contract';

export const ContractItemSchema = z.object({
  contract_item_id: z.string(),
  contract_id: z.string(),
  container_id: z.string(),
  unit_price: z.number(),
  discount_amount: z.number(),
  effective_price: z.number(),
  start_date: z.string(),
  end_date: z.string().optional(),
  status: z.enum(['ACTIVE', 'ENDED', 'CANCELLED', 'active', 'ended', 'cancelled']).catch('ACTIVE'),
  created_at: z.string(),
  updated_at: z.string(),
  deleted_at: z.string().optional()
});

export const ContractSchema = z.object({
  contract_id: z.string(),
  contract_no: z.string(),
  customer_id: z.string(),
  rate_plan_id: z.string().optional(),
  previous_contract_id: z.string().optional(),
  start_date: z.string(),
  end_date: z.string().optional(),
  billing_cycle: z.enum(['monthly', 'quarterly', 'yearly']).catch('monthly'),
  rent_total: z.number(),
  deposit_total: z.number(),
  installment_count: z.number(),
  status: z.enum(['DRAFT', 'ACTIVE', 'ENDING', 'ENDED', 'CANCELLED', 'draft', 'active', 'ending', 'ended', 'cancelled']).catch('ACTIVE'),
  actual_end_date: z.string().optional(),
  pricing_snapshot_json: z.string().optional(),
  terms_snapshot_json: z.string().optional(),
  note: z.string().optional(),
  items: z.array(ContractItemSchema).optional(),
  created_at: z.string(),
  updated_at: z.string(),
  deleted_at: z.string().optional()
});

export const ContractListSchema = z.array(ContractSchema);

export async function fetchContracts(): Promise<Contract[]> {
  const data = await callGasApi<unknown[]>('list', { table: 'contracts' });
  return ContractListSchema.parse(data);
}

export async function createAndActivateContract(input: CreateContractInput & { requestId?: string }): Promise<Contract> {
  const data = await callGasApi<unknown>('activateContract', input as unknown as Record<string, unknown>);
  return ContractSchema.parse(data);
}

export async function renewContract(input: Partial<CreateContractInput> & { previous_contract_id: string; requestId?: string }): Promise<Contract> {
  const data = await callGasApi<unknown>('renewContract', input as unknown as Record<string, unknown>);
  return ContractSchema.parse(data);
}

