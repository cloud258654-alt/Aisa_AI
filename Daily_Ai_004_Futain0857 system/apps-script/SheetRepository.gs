/**
 * Generic Google Sheets access repository
 */

/**
 * Get active spreadsheet using ID stored in properties
 */
function getSpreadsheet() {
  var props = PropertiesService.getScriptProperties();
  var spreadsheetId = props.getProperty('SPREADSHEET_ID');
  if (!spreadsheetId) {
    throw new Error('系統設定錯誤：缺少 SPREADSHEET_ID 參數，請在 Script Properties 中設定。');
  }
  try {
    return SpreadsheetApp.openById(spreadsheetId);
  } catch (e) {
    throw new Error('無法開啟 Google Sheets。請確保 SPREADSHEET_ID 正確且此 Script 有權限讀寫該試算表。原始錯誤: ' + e.toString());
  }
}

/**
 * Get specific sheet by name
 */
function getSheet(tableName) {
  var ss = getSpreadsheet();
  var sheet = ss.getSheetByName(tableName);
  if (!sheet) {
    throw new Error('找不到指定的資料表分頁: ' + tableName);
  }
  return sheet;
}

/**
 * Get primary key column name for a given table
 */
function getIdColumnName(tableName) {
  if (tableName === 'customers') return 'customer_id';
  if (tableName === 'containers') return 'container_id';
  if (tableName === 'rate_plans') return 'rate_plan_id';
  if (tableName === 'contracts') return 'contract_id';
  if (tableName === 'contract_items') return 'contract_item_id';
  if (tableName === 'invoices') return 'invoice_id';
  if (tableName === 'payments') return 'payment_id';
  if (tableName === 'expenses') return 'expense_id';
  if (tableName === 'termination_records') return 'termination_id';
  if (tableName === 'audit_logs') return 'audit_id';
  if (tableName === 'request_logs') return 'request_id';
  if (tableName === 'rental_records') return 'rental_id';
  if (tableName === 'customer_ledgers') return 'ledger_id';
  if (tableName === 'management_ledgers') return 'ledger_id';
  return 'id';
}

/**
 * Get headers of a sheet as a string array
 */
function getHeaders(sheet) {
  var lastCol = sheet.getLastColumn();
  if (lastCol === 0) return [];
  return sheet.getRange(1, 1, 1, lastCol).getValues()[0].map(function(h) {
    return h.toString().trim();
  });
}

/**
 * Convert a sheet row array to a JavaScript Object
 */
function rowToObject(headers, row) {
  var obj = {};
  for (var i = 0; i < headers.length; i++) {
    var val = row[i];
    
    // Convert boolean representation in Sheets
    if (val === true || val === "TRUE") {
      val = true;
    } else if (val === false || val === "FALSE") {
      val = false;
    }
    
    obj[headers[i]] = val;
  }
  return obj;
}

/**
 * Convert a JavaScript Object to a sheet row array based on headers
 */
function objectToRow(headers, obj) {
  var row = [];
  for (var i = 0; i < headers.length; i++) {
    var key = headers[i];
    var val = obj[key];
    if (val === undefined || val === null) {
      row.push('');
    } else if (typeof val === 'boolean') {
      row.push(val ? true : false);
    } else {
      row.push(val);
    }
  }
  return row;
}

/**
 * List all active records in a table (excluding soft-deleted ones)
 */
function listRecords(tableName) {
  var sheet = getSheet(tableName);
  var lastRow = sheet.getLastRow();
  if (lastRow <= 1) return [];

  var headers = getHeaders(sheet);
  var values = sheet.getRange(2, 1, lastRow - 1, headers.length).getValues();
  var records = [];
  var deletedAtIndex = headers.indexOf('deleted_at');

  for (var i = 0; i < values.length; i++) {
    var row = values[i];
    
    // Check if soft deleted (deleted_at is not empty)
    if (deletedAtIndex !== -1 && row[deletedAtIndex] && row[deletedAtIndex].toString().trim() !== '') {
      continue;
    }
    
    records.push(rowToObject(headers, row));
  }
  return records;
}

/**
 * Find record by its primary key ID
 */
function findRecordById(tableName, id) {
  var sheet = getSheet(tableName);
  var lastRow = sheet.getLastRow();
  if (lastRow <= 1) return null;

  var headers = getHeaders(sheet);
  var idColName = getIdColumnName(tableName);
  var idIndex = headers.indexOf(idColName);
  if (idIndex === -1) throw new Error('在 ' + tableName + ' 中找不到 ID 欄位 ' + idColName);

  var values = sheet.getRange(2, 1, lastRow - 1, headers.length).getValues();
  var deletedAtIndex = headers.indexOf('deleted_at');

  for (var i = 0; i < values.length; i++) {
    var row = values[i];
    if (row[idIndex].toString() === id.toString()) {
      // Exclude soft-deleted
      if (deletedAtIndex !== -1 && row[deletedAtIndex] && row[deletedAtIndex].toString().trim() !== '') {
        return null;
      }
      return rowToObject(headers, row);
    }
  }
  return null;
}

/**
 * Create a new record in a table
 */
function createRecord(tableName, record) {
  var sheet = getSheet(tableName);
  var headers = getHeaders(sheet);
  
  // Fill timestamps if missing
  var nowStr = getIsoTimestamp();
  if (!record.created_at) record.created_at = nowStr;
  if (!record.updated_at) record.updated_at = nowStr;
  
  var newRow = objectToRow(headers, record);
  sheet.appendRow(newRow);
  
  // Write to Audit Log
  writeAuditLog('CREATE', tableName, record[getIdColumnName(tableName)], null, record);
  
  return record;
}

/**
 * Update an existing record in a table
 */
function updateRecord(tableName, id, changes) {
  var sheet = getSheet(tableName);
  var lastRow = sheet.getLastRow();
  if (lastRow <= 1) throw new Error('資料表中沒有可更新的資料列');

  var headers = getHeaders(sheet);
  var idColName = getIdColumnName(tableName);
  var idIndex = headers.indexOf(idColName);
  if (idIndex === -1) throw new Error('在 ' + tableName + ' 中找不到 ID 欄位 ' + idColName);

  var values = sheet.getRange(2, 1, lastRow - 1, headers.length).getValues();
  var rowIndex = -1;
  var oldRecord = null;

  for (var i = 0; i < values.length; i++) {
    var row = values[i];
    if (row[idIndex].toString() === id.toString()) {
      rowIndex = i + 2; // Rows are 1-indexed, and we skipped header (row 1)
      oldRecord = rowToObject(headers, row);
      break;
    }
  }

  if (rowIndex === -1 || (oldRecord && oldRecord.deleted_at)) {
    throw new Error('找不到指定 ID 的有效紀錄以進行更新: ' + id);
  }

  // Validate state machine transition if status is changing
  var entityType = getStateMachineEntityType(tableName);
  if (changes.status !== undefined &&
      oldRecord.status !== undefined &&
      entityType) {
    var newStatusUpper = changes.status.toString().toUpperCase();
    validateStatusTransition(
      entityType,
      oldRecord.status,
      newStatusUpper
    );
    changes.status = newStatusUpper;
  }

  // Merge changes
  var updatedRecord = {};
  for (var key in oldRecord) {
    updatedRecord[key] = oldRecord[key];
  }
  for (var changeKey in changes) {
    if (changeKey !== idColName && changeKey !== 'created_at') {
      updatedRecord[changeKey] = changes[changeKey];
    }
  }
  updatedRecord.updated_at = getIsoTimestamp();

  var updatedRow = objectToRow(headers, updatedRecord);
  sheet.getRange(rowIndex, 1, 1, headers.length).setValues([updatedRow]);

  // Write to Audit Log
  writeAuditLog('UPDATE', tableName, id, oldRecord, updatedRecord);

  return updatedRecord;
}

/**
 * Soft delete an existing record
 */
function softDeleteRecord(tableName, id) {
  var nowStr = getIsoTimestamp();
  
  var sheet = getSheet(tableName);
  var lastRow = sheet.getLastRow();
  if (lastRow <= 1) throw new Error('資料表中沒有可刪除的資料列');

  var headers = getHeaders(sheet);
  var idColName = getIdColumnName(tableName);
  var idIndex = headers.indexOf(idColName);
  if (idIndex === -1) throw new Error('在 ' + tableName + ' 中找不到 ID 欄位 ' + idColName);

  var values = sheet.getRange(2, 1, lastRow - 1, headers.length).getValues();
  var rowIndex = -1;
  var oldRecord = null;

  for (var i = 0; i < values.length; i++) {
    var row = values[i];
    if (row[idIndex].toString() === id.toString()) {
      rowIndex = i + 2;
      oldRecord = rowToObject(headers, row);
      break;
    }
  }

  if (rowIndex === -1 || (oldRecord && oldRecord.deleted_at)) {
    throw new Error('找不到指定 ID 的有效紀錄以進行刪除: ' + id);
  }

  var deletedAtIndex = headers.indexOf('deleted_at');
  var updatedAtIndex = headers.indexOf('updated_at');

  if (deletedAtIndex === -1) {
    throw new Error('資料表缺少 deleted_at 欄位，無法進行軟刪除');
  }

  sheet.getRange(rowIndex, deletedAtIndex + 1).setValue(nowStr);
  if (updatedAtIndex !== -1) {
    sheet.getRange(rowIndex, updatedAtIndex + 1).setValue(nowStr);
  }

  var newRecord = {};
  for (var key in oldRecord) {
    newRecord[key] = oldRecord[key];
  }
  newRecord.deleted_at = nowStr;
  newRecord.updated_at = nowStr;

  // Write to Audit Log
  writeAuditLog('DELETE', tableName, id, oldRecord, newRecord);
}

/**
 * Write action details to the audit_logs tab
 */
function writeAuditLog(actionType, tableName, recordId, beforeObj, afterObj) {
  try {
    var sheet = getSheet('audit_logs');
    var headers = getHeaders(sheet);
    
    var auditRecord = {
      audit_id: generateUniqueId('AUD'),
      action: actionType,
      table_name: tableName,
      record_id: recordId,
      before_json: beforeObj ? JSON.stringify(beforeObj) : '',
      after_json: afterObj ? JSON.stringify(afterObj) : '',
      created_at: getIsoTimestamp()
    };
    
    var row = objectToRow(headers, auditRecord);
    sheet.appendRow(row);
  } catch (err) {
    // Fail silently or write to Apps Script console so as not to crash main operation
    console.error('寫入審計日誌失敗:', err);
  }
}

/**
 * Hard delete a record specifically for database failure rollback.
 * ONLY allowed within backend transactional rollback workflows.
 */
function hardDeleteRecordForRollback(tableName, id) {
  var sheet = getSheet(tableName);
  var lastRow = sheet.getLastRow();
  if (lastRow <= 1) return;

  var headers = getHeaders(sheet);
  var idColName = getIdColumnName(tableName);
  var idIndex = headers.indexOf(idColName);
  if (idIndex === -1) return;

  var values = sheet.getRange(2, 1, lastRow - 1, headers.length).getValues();
  for (var i = 0; i < values.length; i++) {
    var row = values[i];
    if (row[idIndex].toString() === id.toString()) {
      var rowIndex = i + 2;
      sheet.deleteRow(rowIndex);
      
      // Log the hard deletion to audit_logs
      writeAuditLog('HARD_DELETE', tableName, id, rowToObject(headers, row), null);
      break;
    }
  }
}
