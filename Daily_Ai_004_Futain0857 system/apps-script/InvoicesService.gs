/**
 * Business logic for invoices management
 */

function createInvoice(data) {
  validateInvoice(data);

  var invoiceId = generateUniqueId('INV');
  var invoiceNo = 'INV-' + formatTodayDateString() + '-' + generateRandomDigits(4);
  var nowStr = getIsoTimestamp();

  var amountDue = Math.round(Number(data.amount_due || 0));
  var amountPaid = Math.round(Number(data.amount_paid || 0));
  var balanceDue = amountDue - amountPaid;

  var status = 'UNPAID';
  if (balanceDue <= 0 && amountDue > 0) {
    status = 'PAID';
  } else if (amountPaid > 0 && balanceDue > 0) {
    status = 'PARTIAL';
  }

  var invoice = {
    invoice_id: invoiceId,
    invoice_no: invoiceNo,
    contract_id: data.contract_id || '',
    customer_id: data.customer_id,
    invoice_type: data.invoice_type || 'rent',
    period_start: data.period_start || '',
    period_end: data.period_end || '',
    due_date: data.due_date || getTodayDateString(),
    amount_due: amountDue,
    amount_paid: amountPaid,
    balance_due: balanceDue,
    status: status,
    note: data.note || '',
    created_at: nowStr,
    updated_at: nowStr,
    voided_at: ''
  };

  return createRecord('invoices', invoice);
}

function updateInvoice(id, updates) {
  var existing = findRecordById('invoices', id);
  if (!existing) {
    throw new AppError('NOT_FOUND', '找不到指定的帳單: ' + id);
  }

  var updated = updateRecord('invoices', id, updates);
  recalculateInvoiceBalance(id);
  return findRecordById('invoices', id);
}

/**
 * Rule 5: amount_paid and balance_due must be recomputed from payment records
 */
function recalculateInvoiceBalance(invoiceId) {
  var invoice = findRecordById('invoices', invoiceId);
  if (!invoice) return null;

  var allPayments = listRecords('payments');
  var totalPaid = 0;

  for (var i = 0; i < allPayments.length; i++) {
    var p = allPayments[i];
    var pStatusUpper = (p.status || '').toString().toUpperCase();
    if (p.invoice_id === invoiceId && (pStatusUpper === 'CONFIRMED' || pStatusUpper === 'COMPLETED') && !p.voided_at) {
      totalPaid += Number(p.amount || 0);
    }
  }

  totalPaid = Math.round(totalPaid);
  var amountDue = Math.round(Number(invoice.amount_due || 0));
  var balanceDue = amountDue - totalPaid;

  var invStatusUpper = (invoice.status || '').toString().toUpperCase();
  var newStatus = invStatusUpper;

  if (invStatusUpper !== 'VOID') {
    if (balanceDue <= 0 && amountDue > 0) {
      newStatus = 'PAID';
    } else if (totalPaid > 0 && balanceDue > 0) {
      newStatus = 'PARTIAL';
    } else {
      newStatus = 'UNPAID';
    }
  }

  updateRecord('invoices', invoiceId, {
    amount_paid: totalPaid,
    balance_due: balanceDue,
    status: newStatus
  });

  return findRecordById('invoices', invoiceId);
}
