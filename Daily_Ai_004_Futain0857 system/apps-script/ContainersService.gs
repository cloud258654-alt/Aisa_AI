/**
 * Service to manage container operations
 */

function createContainer(data) {
  validateContainerInput(data);
  
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
  return updateRecord('containers', id, updates);
}
