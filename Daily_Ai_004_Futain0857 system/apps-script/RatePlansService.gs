/**
 * Business logic for rate_plans management
 */

function createRatePlan(data) {
  validateRatePlan(data);

  var planId = generateUniqueId('RP');
  var nowStr = getIsoTimestamp();

  var ratePlan = {
    rate_plan_id: planId,
    name: data.name,
    container_size_ft: parseInt(data.container_size_ft, 10),
    container_type: data.container_type || 'standard',
    billing_cycle: data.billing_cycle || 'monthly',
    contract_months: parseInt(data.contract_months || 12, 10),
    standard_monthly_price: Math.round(Number(data.standard_monthly_price || 0)),
    contract_price: Math.round(Number(data.contract_price || 0)),
    installment_count: parseInt(data.installment_count || 12, 10),
    default_deposit: Math.round(Number(data.default_deposit || 0)),
    first_year_discount: Math.round(Number(data.first_year_discount || 0)),
    active: data.active !== false,
    note: data.note || '',
    created_at: nowStr,
    updated_at: nowStr,
    deleted_at: ''
  };

  return createRecord('rate_plans', ratePlan);
}

function updateRatePlan(id, updates) {
  var existing = findRecordById('rate_plans', id);
  if (!existing) {
    throw new AppError('NOT_FOUND', '找不到指定的費率方案: ' + id);
  }

  var updatedData = {};
  for (var key in updates) {
    if (key !== 'rate_plan_id' && key !== 'created_at') {
      updatedData[key] = updates[key];
    }
  }

  return updateRecord('rate_plans', id, updatedData);
}
