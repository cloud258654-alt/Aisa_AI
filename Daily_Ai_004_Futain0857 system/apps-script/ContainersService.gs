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
