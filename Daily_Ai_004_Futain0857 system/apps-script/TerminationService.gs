/**
 * Business logic for termination_records, container inspection, and deposit settlement workflows
 */

function startTermination(payload) {
  var requestId = payload.requestId || payload.request_id || '';
  var checkReq = checkAndLockRequestId(requestId, 'startTermination');
  if (checkReq.isDuplicate) {
    return checkReq.previousResult;
  }

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);

  try {
    var contractId = payload.contract_id || payload.id;
    if (!contractId) {
      throw new AppError('BAD_REQUEST', '缺少合約 ID');
    }

    var contract = findRecordById('contracts', contractId);
    if (!contract) {
      throw new AppError('NOT_FOUND', '找不到要辦理退租的合約: ' + contractId);
    }

    // Update Contract status to ENDING
    updateRecord('contracts', contractId, { status: 'ENDING' });

    // Update associated container status to INSPECTION (NOT AVAILABLE)
    var allItems = listRecords('contract_items');
    var updatedContainers = [];
    for (var i = 0; i < allItems.length; i++) {
      var item = allItems[i];
      if (item.contract_id === contractId && (item.status || '').toString().toUpperCase() === 'ACTIVE') {
        updateRecord('containers', item.container_id, { status: 'INSPECTION' });
        updatedContainers.push(item.container_id);
      }
    }

    var result = {
      contract_id: contractId,
      contract_status: 'ENDING',
      containers_in_inspection: updatedContainers
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

function completeContainerInspection(payload) {
  var requestId = payload.requestId || payload.request_id || '';
  var checkReq = checkAndLockRequestId(requestId, 'completeContainerInspection');
  if (checkReq.isDuplicate) {
    return checkReq.previousResult;
  }

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);

  try {
    var containerId = payload.container_id;
    var inspectionStatus = (payload.inspection_status || 'passed').toString().toLowerCase(); // 'passed' | 'failed'
    if (!containerId) {
      throw new AppError('BAD_REQUEST', '缺少貨櫃 ID');
    }

    var container = findRecordById('containers', containerId);
    if (!container) {
      throw new AppError('NOT_FOUND', '找不到指定貨櫃: ' + containerId);
    }

    var newStatus = (inspectionStatus === 'failed') ? 'MAINTENANCE' : 'AVAILABLE';
    var updatedContainer = updateRecord('containers', containerId, {
      status: newStatus,
      note: (container.note ? container.note + ' | ' : '') + '檢查結果: ' + inspectionStatus + ' (' + (payload.note || '') + ')'
    });

    SpreadsheetApp.flush();
    updateRequestIdSuccess(requestId, updatedContainer);
    return updatedContainer;
  } catch (err) {
    updateRequestIdFailed(requestId, err ? (err.code || err.toString()) : 'FAIL');
    throw err;
  } finally {
    lock.releaseLock();
  }
}

function completeTermination(data) {
  var requestId = data.requestId || data.request_id || '';
  var checkReq = checkAndLockRequestId(requestId, 'completeTermination');
  if (checkReq.isDuplicate) {
    return checkReq.previousResult;
  }

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);

  try {
    validateTermination(data);

    var contract = findRecordById('contracts', data.contract_id);
    if (!contract) {
      throw new AppError('NOT_FOUND', '找不到要退租的合約: ' + data.contract_id);
    }

    var terminationId = generateUniqueId('TRM');
    var nowStr = getIsoTimestamp();
    var actualEndDate = data.actual_end_date || getTodayDateString();

    var remoteExpected = parseInt(data.remote_control_expected || 0, 10);
    var remoteReturned = parseInt(data.remote_control_returned || 0, 10);
    var remoteUnitFee = Number(data.remote_control_unit_fee !== undefined ? data.remote_control_unit_fee : 350);
    var missingRemoteFee = Math.max(0, remoteExpected - remoteReturned) * remoteUnitFee;

    var damageFee = Math.round(Number(data.damage_fee || 0));
    var cleaningFee = Math.round(Number(data.cleaning_fee || 0));
    var otherFee = Math.round(Number(data.other_fee || 0));

    var depositOriginal = Math.round(Number(data.deposit_original !== undefined ? data.deposit_original : contract.deposit_total));
    var depositDeducted = Math.round(missingRemoteFee + damageFee + cleaningFee + otherFee);
    var depositRefunded = Math.round(depositOriginal - depositDeducted);

    var record = {
      termination_id: terminationId,
      contract_id: data.contract_id,
      requested_date: data.requested_date || getTodayDateString(),
      actual_end_date: actualEndDate,
      inspection_status: data.inspection_status || 'pending',
      remote_control_expected: remoteExpected,
      remote_control_returned: remoteReturned,
      damage_fee: damageFee,
      cleaning_fee: cleaningFee,
      other_fee: otherFee,
      deposit_original: depositOriginal,
      deposit_deducted: depositDeducted,
      deposit_refunded: depositRefunded,
      settlement_note: data.settlement_note || '',
      status: 'completed',
      created_at: nowStr,
      updated_at: nowStr
    };

    var savedRecord = createRecord('termination_records', record);

    // Update Contract status to ENDED
    updateRecord('contracts', data.contract_id, {
      status: 'ENDED',
      actual_end_date: actualEndDate
    });

    // Update Contract Items and set Container status to INSPECTION (NOT AVAILABLE)
    var allItems = listRecords('contract_items');
    for (var i = 0; i < allItems.length; i++) {
      var item = allItems[i];
      if (item.contract_id === data.contract_id && (item.status || '').toString().toUpperCase() === 'ACTIVE') {
        updateRecord('contract_items', item.contract_item_id, {
          status: 'ENDED',
          end_date: actualEndDate
        });
        
        var currentContainer = findRecordById('containers', item.container_id);
        var curContStatusUpper = currentContainer ? (currentContainer.status || '').toString().toUpperCase() : '';
        if (currentContainer && curContStatusUpper !== 'AVAILABLE' && curContStatusUpper !== 'MAINTENANCE') {
          updateRecord('containers', item.container_id, { status: 'INSPECTION' });
        }
      }
    }

    SpreadsheetApp.flush();
    updateRequestIdSuccess(requestId, savedRecord);
    return savedRecord;
  } catch (err) {
    updateRequestIdFailed(requestId, err ? (err.code || err.toString()) : 'FAIL');
    throw err;
  } finally {
    lock.releaseLock();
  }
}
