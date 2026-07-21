export interface ContractItem {
  contract_item_id: string;
  contract_id: string;
  container_id: string;
  unit_price: number;
  discount_amount: number;
  effective_price: number;
  start_date: string;
  end_date?: string;
  status: 'ACTIVE' | 'ENDED' | 'CANCELLED' | 'active' | 'ended' | 'cancelled';
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}

export type CreateContractItemInput = Omit<ContractItem, 'contract_item_id' | 'contract_id' | 'created_at' | 'updated_at' | 'deleted_at'>;
