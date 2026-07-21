import { ContractItem, CreateContractItemInput } from './contractItem';

export interface Contract {
  contract_id: string;
  contract_no: string;
  customer_id: string;
  rate_plan_id?: string;
  previous_contract_id?: string;
  start_date: string;
  end_date?: string;
  billing_cycle: 'monthly' | 'quarterly' | 'yearly';
  rent_total: number;
  deposit_total: number;
  installment_count: number;
  status: 'DRAFT' | 'ACTIVE' | 'ENDING' | 'ENDED' | 'CANCELLED' | 'draft' | 'active' | 'ending' | 'ended' | 'cancelled';
  actual_end_date?: string;
  pricing_snapshot_json?: string;
  terms_snapshot_json?: string;
  note?: string;
  items?: ContractItem[];
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}

export interface CreateContractInput {
  customer_id: string;
  rate_plan_id?: string;
  previous_contract_id?: string;
  start_date: string;
  end_date?: string;
  billing_cycle?: 'monthly' | 'quarterly' | 'yearly';
  rent_total: number;
  deposit_total: number;
  installment_count?: number;
  status?: 'DRAFT' | 'ACTIVE' | 'draft' | 'active';
  note?: string;
  items: CreateContractItemInput[];
}
