/**
 * Router dispatcher to direct actions to service logic
 */
function routeRequest(action, sessionToken, payload) {
  // Public actions
  if (action === "health") {
    return { ok: true, data: { status: "healthy", timestamp: getIsoTimestamp() }, error: null };
  }
  
  if (action === "login") {
    return handleLoginAction(payload);
  }

  // Authenticated actions check
  var authCheck = verifySessionToken(sessionToken);
  if (!authCheck.valid) {
    return {
      ok: false,
      data: null,
      error: {
        code: "UNAUTHORIZED",
        message: authCheck.message || "登入已逾期，請重新登入"
      }
    };
  }

  // Route authenticated actions
  try {
    switch (action) {
      case "logout":
        return handleLogoutAction(sessionToken);
      case "list":
        return handleListAction(payload);
      case "get":
        return handleGetAction(payload);
      case "create":
        return handleCreateAction(payload);
      case "update":
        return handleUpdateAction(payload);
      case "softDelete":
        return handleSoftDeleteAction(payload);
      case "terminateRental":
        return handleTerminateRentalAction(payload);
      case "dashboardSummary":
        return handleDashboardSummaryAction();
      default:
        throw new AppError("UNKNOWN_ACTION", "未知的 action: " + action);
    }
  } catch (error) {
    console.error("Action " + action + " failed:", error);
    
    // Check if it is a known business error (AppError)
    if (error && error.isAppError) {
      return {
        ok: false,
        data: null,
        error: {
          code: error.code,
          message: error.message
        }
      };
    }
    
    // Internal server errors shouldn't leak sheet details
    return {
      ok: false,
      data: null,
      error: {
        code: "INTERNAL_SERVER_ERROR",
        message: "系統處理失敗，請稍後再試"
      }
    };
  }
}

/**
 * Handle list action
 */
function handleListAction(payload) {
  var table = payload.table;
  if (!table) throw new AppError("BAD_REQUEST", "缺少 table 參數");
  var list = listRecords(table);
  return { ok: true, data: list, error: null };
}

/**
 * Handle get action
 */
function handleGetAction(payload) {
  var table = payload.table;
  var id = payload.id;
  if (!table || !id) throw new AppError("BAD_REQUEST", "缺少 table 或 id 參數");
  var record = findRecordById(table, id);
  if (!record) {
    throw new AppError("NOT_FOUND", "找不到指定的紀錄");
  }
  return { ok: true, data: record, error: null };
}

/**
 * Handle create action
 */
function handleCreateAction(payload) {
  var table = payload.table;
  var data = payload.data;
  if (!table || !data) throw new AppError("BAD_REQUEST", "缺少 table 或 data 參數");

  // Implement route-level lock for safety
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var createdRecord;
    if (table === "customers") {
      createdRecord = createCustomer(data);
    } else if (table === "containers") {
      createdRecord = createContainer(data);
    } else if (table === "rental_records") {
      createdRecord = createRentalRecord(data, payload.createFirstMonthBill);
    } else if (table === "customer_ledgers") {
      createdRecord = createCustomerLedger(data);
    } else if (table === "management_ledgers") {
      createdRecord = createManagementLedger(data);
    } else {
      throw new AppError("BAD_REQUEST", "不支援的寫入資料表: " + table);
    }
    return { ok: true, data: createdRecord, error: null };
  } finally {
    lock.releaseLock();
  }
}

/**
 * Handle update action
 */
function handleUpdateAction(payload) {
  var table = payload.table;
  var id = payload.id;
  var updates = payload.updates;
  if (!table || !id || !updates) throw new AppError("BAD_REQUEST", "缺少 table、id 或 updates 參數");

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var updatedRecord;
    if (table === "customers") {
      updatedRecord = updateCustomer(id, updates);
    } else if (table === "containers") {
      updatedRecord = updateContainer(id, updates);
    } else if (table === "rental_records") {
      updatedRecord = updateRentalRecord(id, updates);
    } else if (table === "customer_ledgers") {
      updatedRecord = updateCustomerLedger(id, updates);
    } else if (table === "management_ledgers") {
      updatedRecord = updateManagementLedger(id, updates);
    } else {
      throw new AppError("BAD_REQUEST", "不支援的更新資料表: " + table);
    }
    return { ok: true, data: updatedRecord, error: null };
  } finally {
    lock.releaseLock();
  }
}

/**
 * Handle softDelete action
 */
function handleSoftDeleteAction(payload) {
  var table = payload.table;
  var id = payload.id;
  if (!table || !id) throw new AppError("BAD_REQUEST", "缺少 table 或 id 參數");

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    softDeleteRecord(table, id);
    return { ok: true, data: { id: id, deleted: true }, error: null };
  } finally {
    lock.releaseLock();
  }
}

/**
 * Handle terminateRental action
 */
function handleTerminateRentalAction(payload) {
  var id = payload.id;
  var endedDate = payload.endedDate;
  var note = payload.note;
  if (!id || !endedDate) throw new AppError("BAD_REQUEST", "缺少 id 或 endedDate 參數");

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var result = terminateRental(id, endedDate, note);
    return { ok: true, data: result, error: null };
  } finally {
    lock.releaseLock();
  }
}

/**
 * Handle dashboardSummary action
 */
function handleDashboardSummaryAction() {
  var summary = getDashboardSummary();
  return { ok: true, data: summary, error: null };
}
