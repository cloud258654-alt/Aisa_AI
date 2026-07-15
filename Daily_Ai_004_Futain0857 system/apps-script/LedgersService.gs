/**
 * Service to manage customer ledgers (invoices/payments) and management ledgers (expenses)
 */

function createCustomerLedger(data) {
  validateCustomerLedgerInput(data);

  var id = generateUniqueId('CL');
  var ledger = {
    ledger_id: id,
    rental_id: data.rental_id,
    customer_id: data.customer_id,
    container_id: data.container_id,
    event_type: data.event_type || 'rent',
    amount: Number(data.amount || 0),
    paid_status: data.paid_status || 'unpaid',
    period_start: data.period_start || '',
    period_end: data.period_end || '',
    due_date: data.due_date || '',
    paid_date: data.paid_date || '',
    payment_method: data.payment_method || '',
    receipt_no: data.receipt_no || '',
    note: data.note || '',
    created_at: getIsoTimestamp(),
    updated_at: getIsoTimestamp(),
    deleted_at: ''
  };

  return createRecord('customer_ledgers', ledger);
}

function updateCustomerLedger(id, updates) {
  validateCustomerLedgerUpdates(updates);
  return updateRecord('customer_ledgers', id, updates);
}

function createManagementLedger(data) {
  validateManagementLedgerInput(data);

  var id = generateUniqueId('ML');
  var ledger = {
    ledger_id: id,
    container_id: data.container_id || '',
    expense_type: data.expense_type || 'other',
    vendor: data.vendor || '',
    amount: Number(data.amount || 0),
    paid_status: data.paid_status || 'paid',
    record_date: data.record_date || '',
    due_date: data.due_date || '',
    paid_date: data.paid_date || '',
    payment_method: data.payment_method || '',
    receipt_no: data.receipt_no || '',
    is_capitalized: data.is_capitalized === true || data.is_capitalized === "TRUE" ? true : false,
    issue_desc: data.issue_desc || '',
    created_at: getIsoTimestamp(),
    updated_at: getIsoTimestamp(),
    deleted_at: ''
  };

  return createRecord('management_ledgers', ledger);
}

function updateManagementLedger(id, updates) {
  validateManagementLedgerUpdates(updates);
  return updateRecord('management_ledgers', id, updates);
}
