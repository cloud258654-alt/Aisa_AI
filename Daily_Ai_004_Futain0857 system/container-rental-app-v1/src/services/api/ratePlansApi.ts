import { z } from 'zod';
import { callGasApi } from './gasClient';
import { RatePlan, CreateRatePlanInput } from '../../types/ratePlan';

export const RatePlanSchema = z.object({
  rate_plan_id: z.string(),
  name: z.string(),
  container_size_ft: z.number(),
  container_type: z.enum(['standard', 'refrigerated', 'open_top']).catch('standard'),
  billing_cycle: z.enum(['monthly', 'quarterly', 'yearly']).catch('monthly'),
  contract_months: z.number(),
  standard_monthly_price: z.number(),
  contract_price: z.number(),
  installment_count: z.number(),
  default_deposit: z.number(),
  first_year_discount: z.number(),
  active: z.boolean(),
  note: z.string().optional(),
  created_at: z.string(),
  updated_at: z.string(),
  deleted_at: z.string().optional()
});

export const RatePlanListSchema = z.array(RatePlanSchema);

export async function fetchRatePlans(): Promise<RatePlan[]> {
  const data = await callGasApi<unknown[]>('list', { table: 'rate_plans' });
  return RatePlanListSchema.parse(data);
}

export async function createRatePlan(input: CreateRatePlanInput): Promise<RatePlan> {
  const data = await callGasApi<unknown>('create', {
    table: 'rate_plans',
    data: input
  });
  return RatePlanSchema.parse(data);
}

export async function updateRatePlan(id: string, updates: Partial<RatePlan>): Promise<RatePlan> {
  const data = await callGasApi<unknown>('update', {
    table: 'rate_plans',
    id,
    updates
  });
  return RatePlanSchema.parse(data);
}

export async function deleteRatePlan(id: string): Promise<void> {
  await callGasApi('softDelete', {
    table: 'rate_plans',
    id
  });
}
