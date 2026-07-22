/**
 * Service to manage container operations
 */

function createContainer(data) {
  validateContainerInput(data);
  
  // Check for duplicate container_no
  var list = listRecords('containers');
  var duplicate = list.some(function(c) {
    return c.container_no === data.container_no;
  });
  if (duplicate) {
    throw new AppError('CONFLICT', '貨櫃編號 ' + data.container_no + ' 已存在，無法重複建立！');
  }

  var id = generateUniqueId('CONT');
  var container = {
    container_id: id,
    container_no: data.container_no,
    size_ft: Number(data.size_ft || 20),
    container_type: data.container_type || 'standard',
    location_zone: data.location_zone || '',
    location_label: data.location_label || '',
    total_setup_cost: Number(data.total_setup_cost || 0),
    status: data.status || 'available',
    note: data.note || '',
    created_at: getIsoTimestamp(),
    updated_at: getIsoTimestamp(),
    deleted_at: ''
  };

  return createRecord('containers', container);
}

function updateContainer(id, updates) {
  validateContainerUpdates(updates);

  if (updates.container_no) {
    var list = listRecords('containers');
    var duplicate = list.some(function(c) {
      return c.container_id !== id && c.container_no === updates.container_no;
    });
    if (duplicate) {
      throw new AppError('CONFLICT', '貨櫃編號 ' + updates.container_no + ' 已存在，無法重複使用！');
    }
  }

  return updateRecord('containers', id, updates);
}

function deleteContainer(id) {
  var container = findRecordById("containers", id);
  if (!container) {
    throw new AppError("NOT_FOUND", "找不到指定的貨櫃");
  }
  
  var status = (container.status || "").toUpperCase();
  if (status === "RENTED" || status === "INSPECTION" || status === "MAINTENANCE") {
    throw new AppError("CONTAINER_NOT_DELETABLE", "貨櫃狀態為 RENTED、INSPECTION 或 MAINTENANCE，無法刪除");
  }
  
  var items = listRecords("contract_items");
  var hasHistory = false;
  for (var i = 0; i < items.length; i++) {
    if (items[i].container_id === id) {
      hasHistory = true;
      break;
    }
  }
  
  if (hasHistory) {
    throw new AppError("CONTAINER_HAS_HISTORICAL_CONTRACT", "該貨櫃有歷史合約紀錄，無法直接刪除，請將狀態改為 RETIRED");
  }
  
  if (status !== "AVAILABLE") {
    throw new AppError("CONTAINER_NOT_AVAILABLE", "只有可用 (AVAILABLE) 狀態的貨櫃可以被刪除");
  }
  
  softDeleteRecord("containers", id);
}
