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
