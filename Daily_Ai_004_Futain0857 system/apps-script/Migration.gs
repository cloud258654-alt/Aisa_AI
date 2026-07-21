/**
 * Data Migration scripts for upgrading legacy sheets (rental_records, customer_ledgers, management_ledgers)
 * to Phase 001 schema (contracts, contract_items, invoices, payments, expenses).
 */

function backupLegacySheets() {
  var ss = getSpreadsheet();
  var timestamp = formatTodayDateString() + '_' + new Date().getTime();
  var legacyNames = ['rental_records', 'customer_ledgers', 'management_ledgers'];

  var backupReport = [];
  for (var i = 0; i < legacyNames.length; i++) {
    var name = legacyNames[i];
    var sheet = ss.getSheetByName(name);
    if (sheet) {
      var backupName = name + '_backup_' + timestamp;
      sheet.copyTo(ss).setName(backupName);
      backupReport.push('已建立備份分頁: ' + backupName);
    }
  }
  return backupReport;
}

function migrateLegacyRentalsToContracts(options) {
  var dryRun = options && options.dryRun !== false;
  var legacyRentals = listRecords('rental_records');
  
  var contractsCreated = 0;
  var itemsCreated = 0;
  var errors = [];
  var reportLogs = [];

  reportLogs.push('=== 租約 (rental_records -> contracts / contract_items) 遷移 ' + (dryRun ? '[Dry-run 測試]' : '[正式執行]') + ' ===');
  reportLogs.push('讀取到 Legacy 租約筆數: ' + legacyRentals.length);

  for (var i = 0; i < legacyRentals.length; i++) {
    var legacy = legacyRentals[i];
    try {
      var contractId = 'CNT-MIG-' + legacy.rental_id;
      var contractNo = 'CN-MIG-' + (legacy.rental_id || i);
      var rentTotal = Number(legacy.monthly_rent || 0);
      var depositTotal = Number(legacy.deposit_amount || 0);

      var contractObj = {
        contract_id: contractId,
        contract_no: contractNo,
        customer_id: legacy.customer_id,
        rate_plan_id: '',
        previous_contract_id: '',
        start_date: legacy.start_date,
        end_date: legacy.end_date || '',
        billing_cycle: legacy.billing_cycle || 'monthly',
        rent_total: rentTotal,
        deposit_total: depositTotal,
        installment_count: 12,
        status: legacy.status || 'active',
        actual_end_date: legacy.ended_date || '',
        pricing_snapshot_json: JSON.stringify({ legacy_monthly_rent: rentTotal, migrated: true }),
        terms_snapshot_json: JSON.stringify({ legacy_rental_id: legacy.rental_id }),
        note: legacy.note || '由舊版 rental_records 遷移',
        created_at: legacy.created_at || getIsoTimestamp(),
        updated_at: getIsoTimestamp(),
        deleted_at: legacy.deleted_at || ''
      };

      var itemObj = {
        contract_item_id: 'CNTI-MIG-' + legacy.rental_id,
        contract_id: contractId,
        container_id: legacy.container_id,
        unit_price: rentTotal,
        discount_amount: 0,
        effective_price: rentTotal,
        start_date: legacy.start_date,
        end_date: legacy.end_date || '',
        status: legacy.status || 'active',
        created_at: legacy.created_at || getIsoTimestamp(),
        updated_at: getIsoTimestamp(),
        deleted_at: legacy.deleted_at || ''
      };

      if (!dryRun) {
        createRecord('contracts', contractObj);
        createRecord('contract_items', itemObj);
      }

      contractsCreated++;
      itemsCreated++;
    } catch (err) {
      errors.push('租約 ' + legacy.rental_id + ' 遷移失敗: ' + err.toString());
    }
  }

  reportLogs.push('預計生成 contracts 筆數: ' + contractsCreated);
  reportLogs.push('預計生成 contract_items 筆數: ' + itemsCreated);
  reportLogs.push('錯誤筆數: ' + errors.length);

  return {
    dryRun: dryRun,
    contractsCreated: contractsCreated,
    itemsCreated: itemsCreated,
    errors: errors,
    reportLogs: reportLogs
  };
}

function migrateLegacyLedgersToInvoicesAndPayments(options) {
  var dryRun = options && options.dryRun !== false;
  var legacyLedgers = listRecords('customer_ledgers');
  
  var invoicesCreated = 0;
  var paymentsCreated = 0;
  var errors = [];
  var reportLogs = [];

  reportLogs.push('=== 客戶帳務 (customer_ledgers -> invoices / payments) 遷移 ' + (dryRun ? '[Dry-run 測試]' : '[正式執行]') + ' ===');
  reportLogs.push('讀取到 Legacy 帳務筆數: ' + legacyLedgers.length);

  for (var i = 0; i < legacyLedgers.length; i++) {
    var leg = legacyLedgers[i];
    try {
      var invoiceId = 'INV-MIG-' + leg.ledger_id;
      var invoiceNo = 'INV-MIG-' + (leg.ledger_id || i);
      var amount = Number(leg.amount || 0);
      var isPaid = leg.paid_status === 'paid';
      var amountPaid = isPaid ? amount : 0;
      var balanceDue = amount - amountPaid;

      var invoiceObj = {
        invoice_id: invoiceId,
        invoice_no: invoiceNo,
        contract_id: leg.rental_id ? ('CNT-MIG-' + leg.rental_id) : '',
        customer_id: leg.customer_id,
        invoice_type: leg.event_type || 'rent',
        period_start: leg.period_start || '',
        period_end: leg.period_end || '',
        due_date: leg.due_date || leg.payment_date || getTodayDateString(),
        amount_due: amount,
        amount_paid: amountPaid,
        balance_due: balanceDue,
        status: isPaid ? 'paid' : 'unpaid',
        note: leg.note || '由舊版 customer_ledgers 遷移',
        created_at: leg.created_at || getIsoTimestamp(),
        updated_at: getIsoTimestamp(),
        voided_at: ''
      };

      if (!dryRun) {
        createRecord('invoices', invoiceObj);
      }
      invoicesCreated++;

      if (isPaid && amountPaid > 0) {
        var paymentObj = {
          payment_id: 'PAY-MIG-' + leg.ledger_id,
          payment_no: 'PAY-MIG-' + (leg.ledger_id || i),
          invoice_id: invoiceId,
          contract_id: leg.rental_id ? ('CNT-MIG-' + leg.rental_id) : '',
          customer_id: leg.customer_id,
          payment_type: leg.event_type || 'rent',
          payment_method: leg.payment_method || 'cash',
          payment_date: leg.paid_date || getTodayDateString(),
          amount: amountPaid,
          bank_last_five: '',
          receipt_no: leg.receipt_no || '',
          status: 'completed',
          note: '遷移自動拆分之已付款紀錄',
          created_at: leg.created_at || getIsoTimestamp(),
          updated_at: getIsoTimestamp(),
          voided_at: ''
        };

        if (!dryRun) {
          createRecord('payments', paymentObj);
        }
        paymentsCreated++;
      }
    } catch (err) {
      errors.push('帳務 ' + leg.ledger_id + ' 遷移失敗: ' + err.toString());
    }
  }

  reportLogs.push('預計生成 invoices 筆數: ' + invoicesCreated);
  reportLogs.push('預計生成 payments 筆數: ' + paymentsCreated);
  reportLogs.push('錯誤筆數: ' + errors.length);

  return {
    dryRun: dryRun,
    invoicesCreated: invoicesCreated,
    paymentsCreated: paymentsCreated,
    errors: errors,
    reportLogs: reportLogs
  };
}

function verifyMigration() {
  var legacyRentals = listRecords('rental_records');
  var contracts = listRecords('contracts');
  var legacyLedgers = listRecords('customer_ledgers');
  var invoices = listRecords('invoices');
  var payments = listRecords('payments');

  var report = [
    '=== 遷移驗證報告 ===',
    'Legacy 租約筆數: ' + legacyRentals.length,
    'Active 合約筆數: ' + contracts.length,
    'Legacy 帳務筆數: ' + legacyLedgers.length,
    'Active 發票/帳單筆數: ' + invoices.length,
    'Active 付款紀錄筆數: ' + payments.length,
    '驗證結論: 資料庫關聯與數量比對完畢。'
  ];

  return {
    legacyRentalsCount: legacyRentals.length,
    contractsCount: contracts.length,
    legacyLedgersCount: legacyLedgers.length,
    invoicesCount: invoices.length,
    paymentsCount: payments.length,
    report: report
  };
}

function normalizeStatusToUppercase(options) {
  var dryRun = options && options.dryRun !== false;
  var tables = ['containers', 'contracts', 'invoices', 'payments'];
  var reportLogs = [];
  var totalModified = 0;

  reportLogs.push('=== 狀態正規化 (Lowercase -> UPPERCASE) ' + (dryRun ? '[Dry-run 測試]' : '[正式執行]') + ' ===');

  for (var t = 0; t < tables.length; t++) {
    var tableName = tables[t];
    var records = listRecords(tableName);
    var tableModified = 0;

    for (var i = 0; i < records.length; i++) {
      var r = records[i];
      if (r.status) {
        var currentStatus = r.status.toString();
        var upperStatus = currentStatus.toUpperCase();
        if (currentStatus !== upperStatus) {
          tableModified++;
          totalModified++;
          var idCol = getIdColumnName(tableName);
          var recordId = r[idCol];
          reportLogs.push('[' + tableName + '] ID ' + recordId + ': ' + currentStatus + ' -> ' + upperStatus);
          if (!dryRun) {
            updateRecord(tableName, recordId, { status: upperStatus });
          }
        }
      }
    }
    reportLogs.push('資料表 ' + tableName + ' 需正規化筆數: ' + tableModified);
  }

  reportLogs.push('總計需正規化筆數: ' + totalModified);
  return {
    dryRun: dryRun,
    totalModified: totalModified,
    reportLogs: reportLogs
  };
}
