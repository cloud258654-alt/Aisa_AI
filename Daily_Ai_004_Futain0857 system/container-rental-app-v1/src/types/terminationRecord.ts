export interface TerminationRecord {
  termination_id: string;
  contract_id: string;
  requested_date: string;
  actual_end_date: string;
  inspection_status: 'passed' | 'failed' | 'pending';
  remote_control_expected: number;
  remote_control_returned: number;
  damage_fee: number;
  cleaning_fee: number;
  other_fee: number;
  deposit_original: number;
  deposit_deducted: number;
  deposit_refunded: number;
  settlement_note?: string;
  status: 'pending' | 'completed';
  created_at: string;
  updated_at: string;
}

export type CreateTerminationRecordInput = Omit<TerminationRecord, 'termination_id' | 'created_at' | 'updated_at'>;
