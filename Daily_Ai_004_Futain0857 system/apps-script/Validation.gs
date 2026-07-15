/**
 * Validations for backend API requests to ensure data integrity
 */

/**
 * Validate customer data fields
 */
function validateCustomerInput(data) {
  if (!data) throw new AppError('VALIDATION_ERROR', '缺少客戶資料內容');
  if (!data.name || data.name.trim() === '') throw new AppError('VALIDATION_ERROR', '客戶名稱為必填欄位');
  
  var type = data.customer_type || 'personal';
  if (type !== 'personal' && type !== 'business') {
    throw new AppError('VALIDATION_ERROR', '無效的客戶類型: ' + type);
  }

  var status = data.status || 'active';
  if (status !== 'active' && status !== 'inactive' && status !== 'blacklisted') {
    throw new AppError('VALIDATION_ERROR', '無效的客戶狀態: ' + status);
  }

  if (data.email && data.email.trim() !== '') {
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      throw new AppError('VALIDATION_ERROR', '電子郵件格式無效');
    }
  }

  // Prevent date/amount fields leaking into customer record
  if (data.amount !== undefined || data.start_date !== undefined || data.end_date !== undefined || data.due_date !== undefined) {
    throw new AppError('VALIDATION_ERROR', '客戶資料中含有不合法的欄位欄值');
  }
}

function validateCustomerUpdates(updates) {
  if (!updates) throw new AppError('VALIDATION_ERROR', '缺少更新內容');
  if (updates.name !== undefined && updates.name.trim() === '') {
    throw new AppError('VALIDATION_ERROR', '客戶名稱不可為空');
  }
  if (updates.customer_type !== undefined && updates.customer_type !== 'personal' && updates.customer_type !== 'business') {
    throw new AppError('VALIDATION_ERROR', '無效的客戶類型: ' + updates.customer_type);
  }
  if (updates.status !== undefined && updates.status !== 'active' && updates.status !== 'inactive' && updates.status !== 'blacklisted') {
    throw new AppError('VALIDATION_ERROR', '無效的客戶狀態: ' + updates.status);
  }
}

/**
 * Validate container data fields
 */
function validateContainerInput(data) {
  if (!data) throw new AppError('VALIDATION_ERROR', '缺少貨櫃資料內容');
  if (!data.container_no || data.container_no.trim() === '') throw new AppError('VALIDATION_ERROR', '貨櫃編號為必填欄位');

  var size = Number(data.size_ft || 0);
  if (isNaN(size) || size <= 0) {
    throw new AppError('VALIDATION_ERROR', '貨櫃尺寸必須大於 0');
  }

  var cost = Number(data.total_setup_cost || 0);
  if (isNaN(cost) || cost < 0) {
    throw new AppError('VALIDATION_ERROR', '建置成本不得小於 0');
  }

  var status = data.status || 'available';
  if (status !== 'available' && status !== 'rented' && status !== 'maintenance' && status !== 'retired') {
    throw new AppError('VALIDATION_ERROR', '無效的貨櫃狀態: ' + status);
  }
}

function validateContainerUpdates(updates) {
  if (!updates) throw new AppError('VALIDATION_ERROR', '缺少更新內容');
  if (updates.container_no !== undefined && updates.container_no.trim() === '') {
    throw new AppError('VALIDATION_ERROR', '貨櫃編號不可為空');
  }
  if (updates.size_ft !== undefined && (isNaN(Number(updates.size_ft)) || Number(updates.size_ft) <= 0)) {
    throw new AppError('VALIDATION_ERROR', '貨櫃尺寸必須大於 0');
  }
  if (updates.total_setup_cost !== undefined && (isNaN(Number(updates.total_setup_cost)) || Number(updates.total_setup_cost) < 0)) {
    throw new AppError('VALIDATION_ERROR', '建置成本不得小於 0');
  }
  if (updates.status !== undefined && updates.status !== 'available' && updates.status !== 'rented' && updates.status !== 'maintenance' && updates.status !== 'retired') {
    throw new AppError('VALIDATION_ERROR', '無效的貨櫃狀態: ' + updates.status);
  }
}

/**
 * Validate rental records
 */
function validateRentalInput(data) {
  if (!data) throw new AppError('VALIDATION_ERROR', '缺少租約資料內容');
  if (!data.customer_id) throw new AppError('VALIDATION_ERROR', '客戶 ID 為必填欄位');
  if (!data.container_id) throw new AppError('VALIDATION_ERROR', '貨櫃 ID 為必填欄位');
  
  if (!data.start_date || !/^\d{4}-\d{2}-\d{2}$/.test(data.start_date)) {
    throw new AppError('VALIDATION_ERROR', '開始日期必須為 YYYY-MM-DD 格式');
  }

  if (data.end_date && data.end_date.trim() !== '') {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(data.end_date)) {
      throw new AppError('VALIDATION_ERROR', '結束日期必須為 YYYY-MM-DD 格式');
    }
    if (data.end_date < data.start_date) {
      throw new AppError('VALIDATION_ERROR', '結束日期不得早於開始日期');
    }
  }

  if (data.monthly_rent !== undefined && (isNaN(Number(data.monthly_rent)) || Number(data.monthly_rent) < 0)) {
    throw new AppError('VALIDATION_ERROR', '月租金不得小於 0');
  }

  if (data.deposit_amount !== undefined && (isNaN(Number(data.deposit_amount)) || Number(data.deposit_amount) < 0)) {
    throw new AppError('VALIDATION_ERROR', '押金金額不得小於 0');
  }

  var dueDay = Number(data.payment_due_day || 1);
  if (isNaN(dueDay) || dueDay < 1 || dueDay > 31) {
    throw new AppError('VALIDATION_ERROR', '繳款日必須限制在 1 至 31 日之間');
  }

  var cycle = data.billing_cycle || 'monthly';
  if (cycle !== 'monthly' && cycle !== 'quarterly' && cycle !== 'yearly') {
    throw new AppError('VALIDATION_ERROR', '無效的計費週期: ' + cycle);
  }

  var status = data.status || 'active';
  if (status !== 'active' && status !== 'ended' && status !== 'cancelled') {
    throw new AppError('VALIDATION_ERROR', '無效的租約狀態: ' + status);
  }
}

function validateRentalUpdates(updates) {
  if (!updates) throw new AppError('VALIDATION_ERROR', '缺少更新內容');
  if (updates.start_date && !/^\d{4}-\d{2}-\d{2}$/.test(updates.start_date)) {
    throw new AppError('VALIDATION_ERROR', '開始日期必須為 YYYY-MM-DD 格式');
  }
  if (updates.end_date && updates.end_date.trim() !== '') {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(updates.end_date)) {
      throw new AppError('VALIDATION_ERROR', '結束日期必須為 YYYY-MM-DD 格式');
    }
  }
  if (updates.monthly_rent !== undefined && (isNaN(Number(updates.monthly_rent)) || Number(updates.monthly_rent) < 0)) {
    throw new AppError('VALIDATION_ERROR', '月租金不得小於 0');
  }
  if (updates.deposit_amount !== undefined && (isNaN(Number(updates.deposit_amount)) || Number(updates.deposit_amount) < 0)) {
    throw new AppError('VALIDATION_ERROR', '押金金額不得小於 0');
  }
  if (updates.status !== undefined && updates.status !== 'active' && updates.status !== 'ended' && updates.status !== 'cancelled') {
    throw new AppError('VALIDATION_ERROR', '無效的租約狀態: ' + updates.status);
  }
}

/**
 * Validate customer billing flow ledger entries
 */
function validateCustomerLedgerInput(data) {
  if (!data) throw new AppError('VALIDATION_ERROR', '缺少帳務資料內容');
  if (!data.customer_id) throw new AppError('VALIDATION_ERROR', '客戶 ID 為必填欄位');
  
  var amount = Number(data.amount || 0);
  if (isNaN(amount) || amount < 0) {
    throw new AppError('VALIDATION_ERROR', '應收金額不得小於 0');
  }

  var paidStatus = data.paid_status || 'unpaid';
  if (paidStatus !== 'paid' && paidStatus !== 'unpaid' && paidStatus !== 'partial') {
    throw new AppError('VALIDATION_ERROR', '無效的入帳狀態: ' + paidStatus);
  }

  var eventType = data.event_type;
  var allowedEvents = ['rent', 'deposit_in', 'deposit_out', 'cleaning_fee', 'adjustment'];
  if (allowedEvents.indexOf(eventType) === -1) {
    throw new AppError('VALIDATION_ERROR', '無效的科目類型: ' + eventType);
  }

  if (paidStatus === 'paid' && (!data.paid_date || data.paid_date.trim() === '')) {
    throw new AppError('VALIDATION_ERROR', '已入帳狀態下必須填寫付款日期');
  }

  if (data.due_date && !/^\d{4}-\d{2}-\d{2}$/.test(data.due_date)) {
    throw new AppError('VALIDATION_ERROR', '截止日期格式無效');
  }
  if (data.paid_date && data.paid_date.trim() !== '' && !/^\d{4}-\d{2}-\d{2}$/.test(data.paid_date)) {
    throw new AppError('VALIDATION_ERROR', '付款日期格式無效');
  }
}

function validateCustomerLedgerUpdates(updates) {
  if (!updates) throw new AppError('VALIDATION_ERROR', '缺少更新內容');
  if (updates.amount !== undefined && (isNaN(Number(updates.amount)) || Number(updates.amount) < 0)) {
    throw new AppError('VALIDATION_ERROR', '金額不得小於 0');
  }
  if (updates.paid_status !== undefined && updates.paid_status !== 'paid' && updates.paid_status !== 'unpaid' && updates.paid_status !== 'partial') {
    throw new AppError('VALIDATION_ERROR', '無效的入帳狀態: ' + updates.paid_status);
  }
  if (updates.paid_status === 'paid' && (!updates.paid_date || updates.paid_date.trim() === '')) {
    throw new AppError('VALIDATION_ERROR', '已入帳狀態下必須提供付款日期');
  }
}

/**
 * Validate management expense entries
 */
function validateManagementLedgerInput(data) {
  if (!data) throw new AppError('VALIDATION_ERROR', '缺少支出資料內容');
  if (!data.vendor || data.vendor.trim() === '') throw new AppError('VALIDATION_ERROR', '廠商名稱為必填欄位');
  
  var amount = Number(data.amount || 0);
  if (isNaN(amount) || amount < 0) {
    throw new AppError('VALIDATION_ERROR', '支出金額不得小於 0');
  }

  var allowedExpenses = ['maintenance', 'land_rent', 'utilities', 'security', 'ads', 'cleaning', 'transport', 'renovation', 'other'];
  if (allowedExpenses.indexOf(data.expense_type) === -1) {
    throw new AppError('VALIDATION_ERROR', '無效的費用種類: ' + data.expense_type);
  }

  if (data.is_capitalized !== true && data.is_capitalized !== false) {
    throw new AppError('VALIDATION_ERROR', '資本化狀態必須是布林值');
  }
}

function validateManagementLedgerUpdates(updates) {
  if (!updates) throw new AppError('VALIDATION_ERROR', '缺少更新內容');
  if (updates.amount !== undefined && (isNaN(Number(updates.amount)) || Number(updates.amount) < 0)) {
    throw new AppError('VALIDATION_ERROR', '金額不得小於 0');
  }
  if (updates.is_capitalized !== undefined && updates.is_capitalized !== true && updates.is_capitalized !== false) {
    throw new AppError('VALIDATION_ERROR', '資本化狀態必須是布林值');
  }
}
