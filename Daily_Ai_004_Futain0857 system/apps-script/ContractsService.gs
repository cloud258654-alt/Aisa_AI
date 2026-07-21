/**
 * Business logic for contracts, contract_items, and renewal workflows
 */

function createAndActivateContract(data) {
  var requestId = data.requestId || data.request_id || '';
  var checkReq = checkAndLockRequestId(requestId, 'activateContract');
  if (checkReq.isDuplicate) {
    return checkReq.previousResult;
  }

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);

  try {
    validateContract(data);

    // 1. Verify customer status inside Lock
    var customer = findRecordById('customers', data.customer_id);
    if (!customer) {
      throw new AppError('NOT_FOUND', '找不到對應客戶: ' + data.customer_id);
    }
    var custStatusUpper = (customer.status || '').toString().toUpperCase();
    if (custStatusUpper !== 'ACTIVE') {
      throw new AppError('VALIDATION_ERROR', '客戶狀態必須為 ACTIVE 才可簽訂合約 (目前狀態: ' + custStatusUpper + ')');
    }

    // 2. Verify rate plan
    var ratePlan = null;
    if (data.rate_plan_id) {
      ratePlan = findRecordById('rate_plans', data.rate_plan_id);
      if (!ratePlan) {
        throw new AppError('NOT_FOUND', '找不到指定的費率方案: ' + data.rate_plan_id);
      }
    }

    // 3. Verify items
    var items = data.items || [];
    if (!Array.isArray(items) || items.length === 0) {
      throw new AppError('BAD_REQUEST', '合約必須包含至少一個貨櫃項目 (items)');
    }

    // 4. Check container availability for each container inside Lock
    for (var i = 0; i < items.length; i++) {
      var item = items[i];
      var container = findRecordById('containers', item.container_id);
      if (!container) {
        throw new AppError('NOT_FOUND', '找不到貨櫃: ' + item.container_id);
      }
      var contStatusUpper = (container.status || '').toString().toUpperCase();
      if (contStatusUpper !== 'AVAILABLE' && !data.previous_contract_id) {
        throw new AppError('CONFLICT', '貨櫃 ' + container.container_no + ' 非空閒狀態 (目前: ' + contStatusUpper + ')');
      }
      checkContainerAvailability(item.container_id, data.start_date, data.end_date, data.previous_contract_id || null);
    }

  var contractId = generateUniqueId('CNT');
  var contractNo = 'CN-' + formatTodayDateString() + '-' + generateRandomDigits(4);
  var nowStr = getIsoTimestamp();

  var rentTotal = Math.round(Number(data.rent_total || 0));
  var depositTotal = Math.round(Number(data.deposit_total || 0));
  var installmentCount = parseInt(data.installment_count || 12, 10);
  if (installmentCount <= 0) installmentCount = 1;

  var pricingSnapshot = {
    rate_plan_name: ratePlan ? ratePlan.name : '自訂方案',
    standard_monthly_price: ratePlan ? ratePlan.standard_monthly_price : (rentTotal / installmentCount),
    contract_price: ratePlan ? ratePlan.contract_price : rentTotal,
    default_deposit: ratePlan ? ratePlan.default_deposit : depositTotal,
    snapshot_at: nowStr
  };

  var termsSnapshot = {
    billing_cycle: data.billing_cycle || 'monthly',
    installment_count: installmentCount,
    items_count: items.length,
    request_id: data.requestId || '',
    snapshot_at: nowStr
  };

  var contractRecord = {
    contract_id: contractId,
    contract_no: contractNo,
    customer_id: data.customer_id,
    rate_plan_id: data.rate_plan_id || '',
    previous_contract_id: data.previous_contract_id || '',
    start_date: data.start_date,
    end_date: data.end_date || '',
    billing_cycle: data.billing_cycle || 'monthly',
    rent_total: rentTotal,
    deposit_total: depositTotal,
    installment_count: installmentCount,
    status: 'active',
    actual_end_date: '',
    pricing_snapshot_json: JSON.stringify(pricingSnapshot),
    terms_snapshot_json: JSON.stringify(termsSnapshot),
    note: data.note || '',
    created_at: nowStr,
    updated_at: nowStr,
    deleted_at: ''
  };

  var savedContract = createRecord('contracts', contractRecord);

  // 5. Create contract items
  var createdItems = [];
  for (var j = 0; j < items.length; j++) {
    var rawItem = items[j];
    var itemId = generateUniqueId('CNTI');
    var contractItem = {
      contract_item_id: itemId,
      contract_id: contractId,
      container_id: rawItem.container_id,
      unit_price: Math.round(Number(rawItem.unit_price || (rentTotal / items.length))),
      discount_amount: Math.round(Number(rawItem.discount_amount || 0)),
      effective_price: Math.round(Number(rawItem.effective_price || rawItem.unit_price || (rentTotal / items.length))),
      start_date: rawItem.start_date || data.start_date,
      end_date: rawItem.end_date || data.end_date || '',
      status: 'active',
      created_at: nowStr,
      updated_at: nowStr,
      deleted_at: ''
    };
    createdItems.push(createRecord('contract_items', contractItem));

    // Update container status to rented
    updateRecord('containers', rawItem.container_id, { status: 'rented' });
  }

  // 6. Generate Deposit Invoice if deposit_total > 0
  var generatedInvoices = [];
  if (depositTotal > 0) {
    var depositInv = createInvoice({
      contract_id: contractId,
      customer_id: data.customer_id,
      invoice_type: 'deposit',
      period_start: data.start_date,
      period_end: data.end_date || data.start_date,
      due_date: data.start_date,
      amount_due: depositTotal,
      amount_paid: 0,
      note: '合約押金帳單 (' + contractNo + ')'
    });
    generatedInvoices.push(depositInv);
  }

  // 7. Generate Installment Rent Invoices
  var installmentAmount = Math.floor(rentTotal / installmentCount);
  var remainder = rentTotal - (installmentAmount * installmentCount);

  for (var k = 0; k < installmentCount; k++) {
    var dueAmt = installmentAmount + (k === 0 ? remainder : 0);
    var rentInv = createInvoice({
      contract_id: contractId,
      customer_id: data.customer_id,
      invoice_type: 'rent',
      period_start: data.start_date,
      period_end: data.end_date || data.start_date,
      due_date: data.start_date,
      amount_due: dueAmt,
      amount_paid: 0,
      note: '租金分期帳單 第 ' + (k + 1) + '/' + installmentCount + ' 期 (' + contractNo + ')'
    });
    generatedInvoices.push(rentInv);
  }

  savedContract.items = createdItems;
  savedContract.invoices = generatedInvoices;

  SpreadsheetApp.flush();
  updateRequestIdSuccess(requestId, savedContract);
  return savedContract;
  } catch (err) {
    updateRequestIdFailed(requestId, err ? (err.code || err.toString()) : 'FAIL');
    throw err;
  } finally {
    lock.releaseLock();
  }
}

function checkContainerAvailability(containerId, startDate, endDate, excludeContractId) {
  var allItems = listRecords('contract_items');
  for (var i = 0; i < allItems.length; i++) {
    var item = allItems[i];
    if (item.container_id === containerId && item.status === 'active') {
      if (excludeContractId && item.contract_id === excludeContractId) {
        continue;
      }
      var itemStart = item.start_date;
      var itemEnd = item.end_date || '9999-12-31';
      var checkEnd = endDate || '9999-12-31';

      if (startDate <= itemEnd && checkEnd >= itemStart) {
        throw new AppError('CONFLICT', '貨櫃 ' + containerId + ' 在此時間段已有重疊有效租約合約項');
      }
    }
  }
}

function updateContract(id, updates) {
  var existing = findRecordById('contracts', id);
  if (!existing) {
    throw new AppError('NOT_FOUND', '找不到指定的合約: ' + id);
  }

  var updated = updateRecord('contracts', id, updates);
  return updated;
}

function renewContract(data) {
  if (!data.previous_contract_id) {
    throw new AppError('BAD_REQUEST', '續約必須提供原合約 ID (previous_contract_id)');
  }

  var prevContract = findRecordById('contracts', data.previous_contract_id);
  if (!prevContract) {
    throw new AppError('NOT_FOUND', '找不到原合約: ' + data.previous_contract_id);
  }

  // Preserve previous contract intact, update status to ended if requested or retain
  updateRecord('contracts', data.previous_contract_id, {
    status: 'ended',
    actual_end_date: data.start_date
  });

  // Create new contract using createAndActivateContract
  var newContractData = {
    customer_id: prevContract.customer_id,
    rate_plan_id: data.rate_plan_id || prevContract.rate_plan_id || '',
    previous_contract_id: data.previous_contract_id,
    start_date: data.start_date,
    end_date: data.end_date || '',
    billing_cycle: data.billing_cycle || prevContract.billing_cycle || 'monthly',
    rent_total: data.rent_total || prevContract.rent_total,
    deposit_total: data.deposit_total || 0, // renewals usually roll over existing deposit
    installment_count: data.installment_count || prevContract.installment_count || 12,
    note: data.note || ('由舊合約 ' + prevContract.contract_no + ' 續約'),
    items: data.items || [],
    requestId: data.requestId || ''
  };

  return createAndActivateContract(newContractData);
}
