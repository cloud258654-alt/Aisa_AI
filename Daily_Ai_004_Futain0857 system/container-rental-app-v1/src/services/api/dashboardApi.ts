import { listContainers } from './containersApi';
import { listRentals } from './rentalsApi';
import { listCustomerLedgers } from './customerLedgersApi';
import { listManagementLedgers } from './managementLedgersApi';
import { parseISO, isSameMonth } from 'date-fns';

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
  try {
    // Parallel load all datasets from Firestore
    const [containers, rentals, customerLedgers, managementLedgers] = await Promise.all([
      listContainers(),
      listRentals(),
      listCustomerLedgers(),
      listManagementLedgers()
    ]);

    const activeContainers = containers.filter(c => !c.deleted_at);
    const total = activeContainers.length;
    const available = activeContainers.filter(c => c.status === 'available').length;
    const rented = activeContainers.filter(c => c.status === 'rented').length;
    const maintenance = activeContainers.filter(c => c.status === 'maintenance').length;
    const retired = activeContainers.filter(c => c.status === 'retired').length;

    const denominator = total - retired;
    const occupancyRate = denominator > 0 ? rented / denominator : 0;

    const activeRentalsList = rentals.filter(r => !r.deleted_at && r.status === 'active');
    const activeRentalsCount = activeRentalsList.length;

    // 30 days calculation
    const now = new Date();
    const thirtyDaysLater = new Date();
    thirtyDaysLater.setDate(now.getDate() + 30);
    let expiring30Days = 0;
    
    activeRentalsList.forEach(r => {
      if (r.end_date) {
        try {
          const endDate = parseISO(r.end_date);
          if (endDate >= now && endDate <= thirtyDaysLater) {
            expiring30Days++;
          }
        } catch {
          return;
        }
      }
    });

    const activeCustomerLedgers = customerLedgers.filter(cl => !cl.deleted_at);
    let monthlyRentCollected = 0;
    let unpaidRent = 0;
    let depositBalance = 0;

    activeCustomerLedgers.forEach(item => {
      const amount = Number(item.amount) || 0;
      
      // Deposit balance
      if (item.paid_status === 'paid') {
        if (item.event_type === 'deposit_in') {
          depositBalance += amount;
        } else if (item.event_type === 'deposit_out') {
          depositBalance -= amount;
        }
      }

      // Monthly collected rent
      if (item.event_type === 'rent' && item.paid_status === 'paid' && item.paid_date) {
        try {
          const paidDate = parseISO(item.paid_date);
          if (isSameMonth(paidDate, now)) {
            monthlyRentCollected += amount;
          }
        } catch {
          return;
        }
      }

      // Unpaid rent
      if (item.event_type === 'rent' && (item.paid_status === 'unpaid' || item.paid_status === 'partial')) {
        unpaidRent += amount;
      }
    });

    const activeManagementLedgers = managementLedgers.filter(ml => !ml.deleted_at);
    let monthlyExpensePaid = 0;

    activeManagementLedgers.forEach(item => {
      const amount = Number(item.amount) || 0;
      if (item.paid_status === 'paid' && item.paid_date) {
        try {
          const paidDate = parseISO(item.paid_date);
          if (isSameMonth(paidDate, now)) {
            monthlyExpensePaid += amount;
          }
        } catch {
          return;
        }
      }
    });

    return {
      total_containers: total,
      available_containers: available,
      rented_containers: rented,
      maintenance_containers: maintenance,
      retired_containers: retired,
      occupancy_rate: Number(occupancyRate.toFixed(2)),
      monthly_rent_collected: monthlyRentCollected,
      monthly_expense_paid: monthlyExpensePaid,
      unpaid_rent: unpaidRent,
      deposit_balance: depositBalance,
      active_rentals: activeRentalsCount,
      expiring_rentals_30_days: expiring30Days
    };
  } catch (error) {
    console.error("Failed to compute getDashboardSummary:", error);
    throw error;
  }
}
