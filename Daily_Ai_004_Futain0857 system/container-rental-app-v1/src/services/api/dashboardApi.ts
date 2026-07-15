import { callGasApi } from './gasClient';

export interface DashboardSummaryData {
  total_containers: number;
  available_containers: number;
  rented_containers: number;
  maintenance_containers: number;
  retired_containers: number;
  occupancy_rate: number;
  monthly_rent_collected: number;
  monthly_expense_paid: number;
  unpaid_rent: number;
  deposit_balance: number;
  active_rentals: number;
  expiring_rentals_30_days: number;
}

export async function getDashboardSummary(): Promise<DashboardSummaryData> {
  return callGasApi<DashboardSummaryData>('dashboardSummary');
}
