/**
 * Business logic for payments management and invoice status updates
 */

function createPayment(data) {
  var requestId = data.requestId || data.request_id || '';
  var checkReq = checkAndLockRequestId(requestId, 'recordPayment');
  if (checkReq.isDuplicate) {
    return checkReq.previousResult;
  }

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);

  try {
    validatePayment(data);

    var paymentId = generateUniqueId('PAY');
    var paymentNo = 'PAY-' + formatTodayDateString() + '-' + generateRandomDigits(4);
    var nowStr = getIsoTimestamp();

    var payment = {
      payment_id: paymentId,
      payment_no: paymentNo,
      invoice_id: data.invoice_id || '',
      contract_id: data.contract_id || '',
      customer_id: data.customer_id,
      payment_type: data.payment_type || 'rent',
      payment_method: data.payment_method || 'bank_transfer',
      payment_date: data.payment_date || getTodayDateString(),
      amount: Math.round(Number(data.amount || 0)),
      bank_last_five: data.bank_last_five || '',
      receipt_no: data.receipt_no || '',
      status: 'CONFIRMED',
      note: data.note || '',
      created_at: nowStr,
      updated_at: nowStr,
      voided_at: ''
    };

    var savedPayment = createRecord('payments', payment);

    var updatedInvoice = null;
    if (data.invoice_id) {
      updatedInvoice = recalculateInvoiceBalance(data.invoice_id);
    }

    var result = {
      payment: savedPayment,
      invoice: updatedInvoice
    };

    SpreadsheetApp.flush();
    updateRequestIdSuccess(requestId, result);
    return result;
  } catch (err) {
    updateRequestIdFailed(requestId, err ? (err.code || err.toString()) : 'FAIL');
    throw err;
  } finally {
    lock.releaseLock();
  }
}

function voidPayment(paymentId, note, requestId) {
  var reqId = requestId || '';
  var checkReq = checkAndLockRequestId(reqId, 'voidPayment');
  if (checkReq.isDuplicate) {
    return checkReq.previousResult;
  }

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);

  try {
    var existing = findRecordById('payments', paymentId);
    if (!existing) {
      throw new AppError('NOT_FOUND', '找不到指定的付款紀錄: ' + paymentId);
    }

    var nowStr = getIsoTimestamp();
    var updated = updateRecord('payments', paymentId, {
      status: 'VOID',
      voided_at: nowStr,
      note: (existing.note ? existing.note + ' | ' : '') + '已作廢: ' + (note || '')
    });

    var updatedInvoice = null;
    if (existing.invoice_id) {
      updatedInvoice = recalculateInvoiceBalance(existing.invoice_id);
    }

    var result = {
      payment: updated,
      invoice: updatedInvoice
    };

    SpreadsheetApp.flush();
    updateRequestIdSuccess(reqId, result);
    return result;
  } catch (err) {
    updateRequestIdFailed(reqId, err ? (err.code || err.toString()) : 'FAIL');
    throw err;
  } finally {
    lock.releaseLock();
  }
}
