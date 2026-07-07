// Management Ledger data type definition (expenses)
export interface ManagementLedger {
  ledger_id: string; // ML-YYYYMMDD-XXXX
  container_id?: string; // Optional ForeignKey containers.container_id (empty for general site expenses)
  expense_type: 'maintenance' | 'land_rent' | 'utilities' | 'security' | 'ads' | 'cleaning' | 'transport' | 'renovation' | 'other';
  vendor: string; // Recipient vendor
  amount: number; // Expense amount
  paid_status: 'paid' | 'unpaid' | 'cancelled';
  record_date: string; // YYYY-MM-DD
  due_date: string; // YYYY-MM-DD
  paid_date: string; // YYYY-MM-DD
  payment_method: string; // e.g., 'cash', 'bank_transfer'
  receipt_no: string; // Invoice/Receipt number or Drive link
  is_capitalized: boolean; // TRUE if it increases asset value, FALSE if normal expense
  issue_desc: string; // Issue/Expense description
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}
