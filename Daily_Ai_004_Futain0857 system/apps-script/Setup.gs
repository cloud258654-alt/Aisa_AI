/**
 * Setup and initialize Google Sheets tabs and metadata
 */

var SCHEMAS = {
  customers: [
    'customer_id', 'name', 'customer_type', 'phone', 'line_id', 
    'email', 'tax_id', 'billing_address', 'status', 'note', 
    'created_at', 'updated_at', 'deleted_at'
  ],
  containers: [
    'container_id', 'container_no', 'size_ft', 'container_type', 
    'location_zone', 'location_label', 'total_setup_cost', 'status', 
    'note', 'created_at', 'updated_at', 'deleted_at'
  ],
  rental_records: [
    'rental_id', 'customer_id', 'container_id', 'start_date', 'end_date', 
    'billing_cycle', 'monthly_rent', 'deposit_amount', 'payment_due_day', 
    'free_period_start', 'free_period_end', 'status', 'ended_date', 
    'note', 'created_at', 'updated_at', 'deleted_at'
  ],
  customer_ledgers: [
    'ledger_id', 'rental_id', 'customer_id', 'container_id', 'event_type', 
    'amount', 'paid_status', 'period_start', 'period_end', 'due_date', 
    'paid_date', 'payment_method', 'receipt_no', 'note', 'created_at', 
    'updated_at', 'deleted_at'
  ],
  management_ledgers: [
    'ledger_id', 'container_id', 'expense_type', 'vendor', 'amount', 
    'paid_status', 'record_date', 'due_date', 'paid_date', 'payment_method', 
    'receipt_no', 'is_capitalized', 'issue_desc', 'created_at', 'updated_at', 
    'deleted_at'
  ],
  audit_logs: [
    'audit_id', 'action', 'table_name', 'record_id', 
    'before_json', 'after_json', 'created_at'
  ]
};

/**
 * Initialize Spreadsheet tabs, headers, and frozen rows.
 * Can be run repeatedly without losing existing data.
 */
function setupSpreadsheet() {
  var ss = getSpreadsheet();
  
  for (var tableName in SCHEMAS) {
    var requiredHeaders = SCHEMAS[tableName];
    var sheet = ss.getSheetByName(tableName);
    
    // Create tab if it doesn't exist
    if (!sheet) {
      sheet = ss.insertSheet(tableName);
    }
    
    var lastCol = sheet.getLastColumn();
    var currentHeaders = [];
    
    if (lastCol > 0) {
      currentHeaders = sheet.getRange(1, 1, 1, lastCol).getValues()[0].map(function(h) {
        return h.toString().trim();
      });
    }
    
    // Determine headers to append
    var headersToAppend = [];
    for (var i = 0; i < requiredHeaders.length; i++) {
      var req = requiredHeaders[i];
      if (currentHeaders.indexOf(req) === -1) {
        headersToAppend.push(req);
      }
    }
    
    // Append missing headers
    if (currentHeaders.length === 0) {
      // Setup fresh headers
      sheet.getRange(1, 1, 1, requiredHeaders.length).setValues([requiredHeaders]);
      sheet.setFrozenRows(1);
    } else if (headersToAppend.length > 0) {
      // Append new columns to the end
      sheet.getRange(1, currentHeaders.length + 1, 1, headersToAppend.length).setValues([headersToAppend]);
    }
    
    // Refresh last column after appends
    var finalColCount = sheet.getLastColumn();
    
    // Apply styling to headers
    var headerRange = sheet.getRange(1, 1, 1, finalColCount);
    headerRange.setFontWeight('bold');
    headerRange.setBackground('#f3f4f6'); // Tailwind gray-100
    headerRange.setFontColor('#1f2937'); // Tailwind gray-800
    headerRange.setHorizontalAlignment('left');
  }
  
  Logger.log('試算表初始化設定成功！');
}

/**
 * Help administrators configure required Script Properties in Google Apps Script Console
 */
function setupScriptPropertiesExample() {
  var propsNeeded = [
    'SPREADSHEET_ID',
    'ADMIN_USERNAME',
    'PASSWORD_SALT',
    'PASSWORD_HASH',
    'SESSION_SECRET',
    'SESSION_TTL_SECONDS'
  ];
  
  Logger.log('=== Google Apps Script 專案設定說明 ===');
  Logger.log('請於專案設定 (Project Settings) ➔ 指令碼屬性 (Script Properties) 中設定以下變數：');
  for (var i = 0; i < propsNeeded.length; i++) {
    Logger.log('- ' + propsNeeded[i]);
  }
  Logger.log('註：PASSWORD_HASH 可以透過執行此專案的密碼產生器 (如 hashPassword 函式) 進行雜湊後填入。');
}
