/**
 * Service to manage customer operations
 */

function createCustomer(data) {
  validateCustomerInput(data);
  
  var id = generateUniqueId('CUST');
  var customer = {
    customer_id: id,
    name: data.name,
    customer_type: data.customer_type || 'personal',
    phone: data.phone || '',
    line_id: data.line_id || '',
    email: data.email || '',
    tax_id: data.tax_id || '',
    billing_address: data.billing_address || '',
    status: data.status || 'active',
    note: data.note || '',
    created_at: getIsoTimestamp(),
    updated_at: getIsoTimestamp(),
    deleted_at: ''
  };

  return createRecord('customers', customer);
}

function updateCustomer(id, updates) {
  validateCustomerUpdates(updates);
  return updateRecord('customers', id, updates);
}

function deleteCustomer(id) {
  var contracts = listRecords("contracts");
  var hasActive = false;
  var hasHistorical = false;
  
  for (var i = 0; i < contracts.length; i++) {
    var contract = contracts[i];
    if (contract.customer_id === id) {
      var status = (contract.status || "").toUpperCase();
      if (status === "ACTIVE" || status === "ENDING" || status === "DRAFT") {
        hasActive = true;
      } else {
        hasHistorical = true;
      }
    }
  }
  
  if (hasActive) {
    throw new AppError("CUSTOMER_HAS_ACTIVE_CONTRACT", "該客戶目前有進行中或草稿合約，無法刪除");
  }
  if (hasHistorical) {
    throw new AppError("CUSTOMER_HAS_HISTORICAL_CONTRACT", "該客戶有歷史合約紀錄，無法直接刪除，請將狀態改為 INACTIVE");
  }
  
  softDeleteRecord("customers", id);
}
