/**
 * Idempotency control using request_logs table
 */

function checkAndLockRequestId(requestId, actionName) {
  if (!requestId || requestId.toString().trim() === '') {
    return { isDuplicate: false, previousResult: null };
  }

  var reqId = requestId.toString().trim();
  var sheet = getSheet('request_logs');
  var existing = findRecordById('request_logs', reqId);

  if (existing) {
    var status = existing.status ? existing.status.toString().toUpperCase() : '';
    if (status === 'PROCESSING') {
      throw new AppError('DUPLICATE_REQUEST', '請求 (requestId: ' + reqId + ') 正在處理中，請勿重複提交');
    }
    if (status === 'SUCCESS') {
      var cachedData = null;
      if (existing.result_record_id) {
        try {
          cachedData = JSON.parse(existing.result_record_id);
        } catch (e) {
          cachedData = { record_id: existing.result_record_id };
        }
      }
      return { isDuplicate: true, previousResult: cachedData };
    }
    if (status === 'FAILED') {
      throw new AppError('DUPLICATE_REQUEST', '請求 (requestId: ' + reqId + ') 先前執行失敗，請更換新的 requestId 重新嘗試');
    }
  }

  // Create PROCESSING record
  var nowStr = getIsoTimestamp();
  var reqLog = {
    request_id: reqId,
    action: actionName || 'unknown',
    status: 'PROCESSING',
    result_record_id: '',
    error_code: '',
    created_at: nowStr,
    updated_at: nowStr,
    expires_at: ''
  };

  createRecord('request_logs', reqLog);
  SpreadsheetApp.flush();
  return { isDuplicate: false, previousResult: null };
}

function updateRequestIdSuccess(requestId, resultObj) {
  if (!requestId || requestId.toString().trim() === '') return;
  var reqId = requestId.toString().trim();
  var nowStr = getIsoTimestamp();

  var resultJson = typeof resultObj === 'object' ? JSON.stringify(resultObj) : String(resultObj);
  updateRecord('request_logs', reqId, {
    status: 'SUCCESS',
    result_record_id: resultJson,
    updated_at: nowStr
  });
  SpreadsheetApp.flush();
}

function updateRequestIdFailed(requestId, errorCode) {
  if (!requestId || requestId.toString().trim() === '') return;
  var reqId = requestId.toString().trim();
  var nowStr = getIsoTimestamp();

  updateRecord('request_logs', reqId, {
    status: 'FAILED',
    error_code: errorCode || 'INTERNAL_ERROR',
    updated_at: nowStr
  });
  SpreadsheetApp.flush();
}
