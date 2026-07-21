// Container data type definition with Canonical Uppercase status values
export interface Container {
  container_id: string; // CONT-YYYYMMDD-XXXX
  container_no: string; // Container number (e.g., A001, B002)
  size_ft: number; // Size in feet (e.g., 20, 40)
  container_type: string; // e.g., 'standard', 'refrigerated', 'open_top'
  location_zone: string; // e.g., 'Zone A', 'Zone B'
  location_label: string; // e.g., 'A-12', 'B-05'
  total_setup_cost: number; // Initial acquisition + setup cost
  status: 'AVAILABLE' | 'RESERVED' | 'RENTED' | 'INSPECTION' | 'MAINTENANCE' | 'BLOCKED' | 'RETIRED' | 'available' | 'rented' | 'maintenance' | 'retired' | 'inspection';
  note: string;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}
