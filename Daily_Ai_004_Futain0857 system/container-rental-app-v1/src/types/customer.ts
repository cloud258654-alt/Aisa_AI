// Customer data type definition
export interface Customer {
  customer_id: string; // CUST-YYYYMMDD-XXXX
  name: string; // Customer name or company name
  customer_type: 'personal' | 'business';
  phone: string;
  line_id: string;
  email: string;
  tax_id: string; // Unified business number (for business customers)
  billing_address: string;
  status: 'active' | 'inactive' | 'blacklisted';
  note: string;
  created_at: string; // ISO date-time string
  updated_at: string; // ISO date-time string
  deleted_at?: string; // Optional soft-delete timestamp
}
