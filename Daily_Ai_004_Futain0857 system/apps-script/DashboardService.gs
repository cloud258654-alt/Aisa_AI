/**
 * Service to aggregate dashboard metrics directly from Sheets data
 */

function getDashboardSummary() {
  var containers = listRecords('containers');
  var rentals = listRecords('rental_records');
  var customerLedgers = listRecords('customer_ledgers');
  var managementLedgers = listRecords('management_ledgers');

  var now = new Date();
  var currentYear = now.getFullYear();
  var currentMonth = now.getMonth(); // 0-indexed

  // 1. Containers counts
  var total = 0;
  var rented = 0;
  var available = 0;
  var maintenance = 0;
  var retired = 0;

  for (var i = 0; i < containers.length; i++) {
    var c = containers[i];
    if (c.status === 'retired') {
      retired++;
    } else {
      total++;
      if (c.status === 'rented') rented++;
      else if (c.status === 'available') available++;
      else if (c.status === 'maintenance') maintenance++;
    }
  }

  var occupancy = total === 0 ? 0 : rented / total;

  // 2. Revenue collected this month (rent paid this month)
  var monthlyRentCollected = 0;
  for (var j = 0; j < customerLedgers.length; j++) {
    var cl = customerLedgers[j];
    if (cl.event_type === 'rent' && cl.paid_status === 'paid' && cl.paid_date) {
      var paidDate = parseDateString(cl.paid_date);
      if (paidDate && paidDate.getFullYear() === currentYear && paidDate.getMonth() === currentMonth) {
        monthlyRentCollected += Number(cl.amount || 0);
      }
    }
  }

  // 3. Unpaid rent (receivables)
  var unpaidRent = 0;
  for (var k = 0; k < customerLedgers.length; k++) {
    var cl2 = customerLedgers[k];
    if (cl2.event_type === 'rent' && (cl2.paid_status === 'unpaid' || cl2.paid_status === 'partial')) {
      unpaidRent += Number(cl2.amount || 0);
    }
  }

  // 4. Deposit balance (held)
  var depositBalance = 0;
  for (var l = 0; l < customerLedgers.length; l++) {
    var cl3 = customerLedgers[l];
    if (cl3.paid_status === 'paid') {
      if (cl3.event_type === 'deposit_in') {
        depositBalance += Number(cl3.amount || 0);
      } else if (cl3.event_type === 'deposit_out') {
        depositBalance -= Number(cl3.amount || 0);
      }
    }
  }

  // 5. Monthly management expense paid this month
  var monthlyExpensePaid = 0;
  for (var m = 0; m < managementLedgers.length; m++) {
    var ml = managementLedgers[m];
    if (ml.paid_status === 'paid' && ml.paid_date) {
      var expPaidDate = parseDateString(ml.paid_date);
      if (expPaidDate && expPaidDate.getFullYear() === currentYear && expPaidDate.getMonth() === currentMonth) {
        monthlyExpensePaid += Number(ml.amount || 0);
      }
    }
  }

  // 6. Active rentals count
  var activeRentals = 0;
  for (var n = 0; n < rentals.length; n++) {
    if (rentals[n].status === 'active') {
      activeRentals++;
    }
  }

  // 7. Expiring rentals within 30 days
  var expiringRentals30Days = 0;
  var thirtyDaysLater = new Date();
  thirtyDaysLater.setDate(now.getDate() + 30);

  for (var p = 0; p < rentals.length; p++) {
    var r = rentals[p];
    if (r.status === 'active' && r.end_date) {
      var endDate = parseDateString(r.end_date);
      if (endDate && endDate >= now && endDate <= thirtyDaysLater) {
        expiringRentals30Days++;
      }
    }
  }

  return {
    occupancy_rate: occupancy,
    total_containers: total + retired,
    rented_containers: rented,
    available_containers: available,
    maintenance_containers: maintenance,
    retired_containers: retired,
    monthly_rent_collected: monthlyRentCollected,
    unpaid_rent: unpaidRent,
    deposit_balance: depositBalance,
    monthly_expense_paid: monthlyExpensePaid,
    active_rentals: activeRentals,
    expiring_rentals_30_days: expiringRentals30Days
  };
}
