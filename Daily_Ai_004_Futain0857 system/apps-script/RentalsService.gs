/**
 * Service to manage rental agreements and leases
 */

function createRentalRecord(data, createFirstMonthBill) {
  validateRentalInput(data);

  // 1. Check customer exists
  var customer = findRecordById('customers', data.customer_id);
  if (!customer) {
    throw new AppError('NOT_FOUND', '指定客戶不存在！');
  }

  // 2. Check container exists and is available
  var container = findRecordById('containers', data.container_id);
  if (!container) {
    throw new AppError('NOT_FOUND', '指定貨櫃不存在！');
  }
  if (container.status !== 'available') {
    throw new AppError('CONFLICT', '貨櫃 ' + container.container_no + ' 狀態為「' + container.status + '」，目前無法出租！');
  }

  // 3. Check for conflicting active rentals
  var activeRentals = listRecords('rental_records');
  var conflict = activeRentals.some(function(r) {
    return r.container_id === data.container_id && r.status === 'active';
  });
  if (conflict) {
    throw new AppError('CONFLICT', '該貨櫃目前已有生效中的租賃合約，無法重複出租！');
  }

  // Save the original container status for precise rollback
  var originalContainerStatus = container.status;

  // 4. Create the rental record
  var rentalId = generateUniqueId('RENT');
  var nowStr = getIsoTimestamp();
  
  var rental = {
    rental_id: rentalId,
    customer_id: data.customer_id,
    container_id: data.container_id,
    start_date: data.start_date, // YYYY-MM-DD
    end_date: data.end_date, // YYYY-MM-DD
    billing_cycle: data.billing_cycle || 'monthly',
    monthly_rent: Number(data.monthly_rent || 0),
    deposit_amount: Number(data.deposit_amount || 0),
    payment_due_day: Number(data.payment_due_day || 1),
    free_period_start: data.free_period_start || '',
    free_period_end: data.free_period_end || '',
    status: data.status || 'active',
    ended_date: '',
    note: data.note || '',
    created_at: nowStr,
    updated_at: nowStr,
    deleted_at: ''
  };

  var completedSteps = [];
  var createdDepositId = null;
  var createdRentId = null;

  try {
    // Step A: Save rental record
    createRecord('rental_records', rental);
    completedSteps.push('rental_created');

    // Step B: Update container status to 'rented'
    updateRecord('containers', data.container_id, { status: 'rented' });
    completedSteps.push('container_updated');

    // Step C: Generate bills
    if (createFirstMonthBill) {
      var rentAmount = Number(rental.monthly_rent);
      var depositAmount = Number(rental.deposit_amount);

      var startDate = parseDateString(rental.start_date);
      
      // Calculate first month period end (add 1 month, subtract 1 day)
      var endPeriodDate = new Date(startDate.getTime());
      endPeriodDate.setMonth(endPeriodDate.getMonth() + 1);
      endPeriodDate.setDate(endPeriodDate.getDate() - 1);
      var endPeriodStr = formatDateString(endPeriodDate);

      // Calculate due date (payment_due_day of the current month)
      var dueDay = rental.payment_due_day;
      var dueDate = new Date(startDate.getFullYear(), startDate.getMonth(), dueDay);
      // If due date is earlier than start_date, or invalid, default to start_date
      if (isNaN(dueDate.getTime()) || dueDate < startDate) {
        dueDate = startDate;
      }
      var dueDateStr = formatDateString(dueDate);

      // Deposit Entry (deposit_in)
      if (depositAmount > 0) {
        createdDepositId = generateUniqueId('CL');
        var depositLedger = {
          ledger_id: createdDepositId,
          rental_id: rentalId,
          customer_id: rental.customer_id,
          container_id: rental.container_id,
          event_type: 'deposit_in',
          amount: depositAmount,
          paid_status: 'unpaid',
          period_start: rental.start_date,
          period_end: rental.start_date,
          due_date: rental.start_date,
          paid_date: '',
          payment_method: '',
          receipt_no: '',
          note: '租賃押金應收',
          created_at: nowStr,
          updated_at: nowStr,
          deleted_at: ''
        };
        createRecord('customer_ledgers', depositLedger);
        completedSteps.push('deposit_created');
      }

      // First Month Rent Entry (rent)
      if (rentAmount > 0) {
        createdRentId = generateUniqueId('CL');
        var rentLedger = {
          ledger_id: createdRentId,
          rental_id: rentalId,
          customer_id: rental.customer_id,
          container_id: rental.container_id,
          event_type: 'rent',
          amount: rentAmount,
          paid_status: 'unpaid',
          period_start: rental.start_date,
          period_end: endPeriodStr,
          due_date: dueDateStr,
          paid_date: '',
          payment_method: '',
          receipt_no: '',
          note: '首期租金 (' + rental.start_date + ' ~ ' + endPeriodStr + ')',
          created_at: nowStr,
          updated_at: nowStr,
          deleted_at: ''
        };
        createRecord('customer_ledgers', rentLedger);
        completedSteps.push('rent_created');
      }
    }

    writeAuditLog('RENTAL_WORKFLOW_COMPLETED', 'rental_records', rentalId, null, rental);
    return rental;

  } catch (error) {
    console.error("Lease creation failed, starting rollback. Error:", error);
    
    // Execute rollback actions in reverse order of creation
    try {
      if (completedSteps.indexOf('rent_created') !== -1 && createdRentId) {
        hardDeleteRecordForRollback('customer_ledgers', createdRentId);
      }
      if (completedSteps.indexOf('deposit_created') !== -1 && createdDepositId) {
        hardDeleteRecordForRollback('customer_ledgers', createdDepositId);
      }
      if (completedSteps.indexOf('container_updated') !== -1) {
        updateRecord('containers', data.container_id, { status: originalContainerStatus });
      }
      if (completedSteps.indexOf('rental_created') !== -1) {
        hardDeleteRecordForRollback('rental_records', rentalId);
      }
      writeAuditLog('RENTAL_WORKFLOW_ROLLED_BACK', 'rental_records', rentalId, null, { error: error.message || error.toString() });
    } catch (rollbackError) {
      console.error("FATAL: Rollback failed! Re-throwing original error. Rollback error:", rollbackError);
      writeAuditLog('ROLLBACK_FAILED', 'rental_records', rentalId, null, { 
        originalError: error.message || error.toString(),
        rollbackError: rollbackError.message || rollbackError.toString()
      });
    }

    // Rethrow original error
    throw error;
  }
}

function updateRentalRecord(id, updates) {
  validateRentalUpdates(updates);
  return updateRecord('rental_records', id, updates);
}

function terminateRental(id, endedDate, note) {
  var rental = findRecordById('rental_records', id);
  if (!rental) {
    throw new AppError('NOT_FOUND', '找不到指定的租賃紀錄！ ID: ' + id);
  }
  if (rental.status !== 'active') {
    throw new AppError('CONFLICT', '該租賃合約目前不是生效狀態，無法退租！目前狀態：' + rental.status);
  }

  var container = findRecordById('containers', rental.container_id);
  var originalContainerStatus = container ? container.status : 'rented';

  // Backup original status and values for potential rollback
  var beforeSnapshot = {
    status: rental.status,
    ended_date: rental.ended_date || '',
    note: rental.note || '',
    updated_at: rental.updated_at || ''
  };

  var completedSteps = [];

  try {
    // 1. Update rental status
    var terminatedNote = note ? (rental.note ? rental.note + '\n退租備註: ' + note : '退租備註: ' + note) : rental.note;
    var updatedRental = updateRecord('rental_records', id, {
      status: 'ended',
      ended_date: endedDate,
      note: terminatedNote
    });
    completedSteps.push('rental_updated');

    // 2. Revert container status to 'available'
    updateRecord('containers', rental.container_id, { status: 'available' });
    completedSteps.push('container_updated');

    writeAuditLog('TERMINATION_WORKFLOW_COMPLETED', 'rental_records', id, beforeSnapshot, updatedRental);
    return updatedRental;

  } catch (error) {
    console.error("Termination failed, rolling back. Error:", error);
    try {
      if (completedSteps.indexOf('container_updated') !== -1) {
        updateRecord('containers', rental.container_id, { status: originalContainerStatus });
      }
      if (completedSteps.indexOf('rental_updated') !== -1) {
        updateRecord('rental_records', id, beforeSnapshot);
      }
      writeAuditLog('TERMINATION_ROLLED_BACK', 'rental_records', id, beforeSnapshot, null);
    } catch (rollbackError) {
      console.error("FATAL: Rollback of termination failed! Error:", rollbackError);
      writeAuditLog('ROLLBACK_FAILED', 'rental_records', id, beforeSnapshot, { 
        originalError: error.message || error.toString(),
        rollbackError: rollbackError.message || rollbackError.toString()
      });
    }
    throw error;
  }
}
