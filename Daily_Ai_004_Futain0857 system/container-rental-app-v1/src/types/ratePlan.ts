export interface RatePlan {
  rate_plan_id: string;
  name: string;
  container_size_ft: number;
  container_type: 'standard' | 'refrigerated' | 'open_top';
  billing_cycle: 'monthly' | 'quarterly' | 'yearly';
  contract_months: number;
  standard_monthly_price: number;
  contract_price: number;
  installment_count: number;
  default_deposit: number;
  first_year_discount: number;
  active: boolean;
  note?: string;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}

export type CreateRatePlanInput = Omit<RatePlan, 'rate_plan_id' | 'created_at' | 'updated_at' | 'deleted_at'>;
