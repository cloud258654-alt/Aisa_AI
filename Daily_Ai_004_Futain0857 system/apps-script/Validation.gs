/**
 * Validations for backend API requests to ensure data integrity
 */

function validateCustomerInput(data) {
  if (!data) throw new Error('缺少客戶資料內容');
  if (!data.name || data.name.trim() === '') throw new Error('客戶名稱為必填欄位');
  var type = data.customer_type;
  if (type && type !== 'personal' && type !== 'business') {
    throw new Error('無效的客戶類型: ' + type);
  }
}

function validateCustomerUpdates(updates) {
  if (!updates) throw new Error('缺少更新內容');
  if (updates.name !== undefined && updates.name.trim() === '') {
    throw new Error('客戶名稱不可為空');
  }
}

function validateContainerInput(data) {
  if (!data) throw new Error('缺少貨櫃資料內容');
  if (!data.container_no || data.container_no.trim() === '') throw new Error('貨櫃編號為必填欄位');
}

function validateContainerUpdates(updates) {
  if (!updates) throw new Error('缺少更新內容');
  if (updates.container_no !== undefined && updates.container_no.trim() === '') {
    throw new Error('貨櫃編號不可為空');
  }
}

function validateRentalInput(data) {
  if (!data) throw new Error('缺少租約資料內容');
  if (!data.customer_id) throw new Error('客戶 ID 為必填欄位');
  if (!data.container_id) throw new Error('貨櫃 ID 為必填欄位');
  if (!data.start_date || !/^\d{4}-\d{2}-\d{2}$/.test(data.start_date)) {
    throw new Error('開始日期必須為 YYYY-MM-DD 格式');
  }
}

function validateRentalUpdates(updates) {
  if (!updates) throw new Error('缺少更新內容');
  if (updates.start_date && !/^\d{4}-\d{2}-\d{2}$/.test(updates.start_date)) {
    throw new Error('開始日期必須為 YYYY-MM-DD 格式');
  }
}

function validateCustomerLedgerInput(data) {
  if (!data) throw new Error('缺少帳務資料內容');
  if (!data.customer_id) throw new Error('客戶 ID 為必填欄位');
  if (data.amount === undefined || isNaN(Number(data.amount))) throw new Error('金額必須為有效數字');
}

function validateCustomerLedgerUpdates(updates) {
  if (!updates) throw new Error('缺少更新內容');
  if (updates.amount !== undefined && isNaN(Number(updates.amount))) {
    throw new Error('金額必須為有效數字');
  }
}

function validateManagementLedgerInput(data) {
  if (!data) throw new Error('缺少支出資料內容');
  if (!data.vendor || data.vendor.trim() === '') throw new Error('廠商名稱為必填欄位');
  if (data.amount === undefined || isNaN(Number(data.amount))) throw new Error('金額必須為有效數字');
}

function validateManagementLedgerUpdates(updates) {
  if (!updates) throw new Error('缺少更新內容');
  if (updates.amount !== undefined && isNaN(Number(updates.amount))) {
    throw new Error('金額必須為有效數字');
  }
}
