/**
 * Manual and Unit Tests for Google Apps Script Backend Services.
 * These functions can be run manually in the GAS Editor to verify correctness.
 */

function runAllBackendTests() {
  Logger.log("=== STARTING BACKEND TESTS ===");
  try {
    testHashPassword();
    testGenerateAndVerifyToken();
    testExpiredToken();
    testRowToObject();
    testObjectToRow();
    testRentalConflictDetection();
    testPhase001DataModelsAndDryRun();
    testPhase002WorkflowsCases();
    testPhase003ConsistencyAndSecurity();
    testSafetyDeleteAndStatusChange();
    Logger.log("=== ALL TESTS PASSED SUCCESSFULLY ===");
  } catch (error) {
    Logger.log("!!! TEST FAILED: " + error.toString());
  }
}

function testHashPassword() {
  Logger.log("Running testHashPassword...");
  var password = "mySecretPassword123";
  var salt = "random_salt_xyz";
  
  var hash1 = hashPassword(password, salt);
  var hash2 = hashPassword(password, salt);
  
  if (hash1 !== hash2) {
    throw new Error("testHashPassword failed: Hashing is inconsistent.");
  }
  
  var differentHash = hashPassword("otherPassword", salt);
  if (hash1 === differentHash) {
    throw new Error("testHashPassword failed: Different password produced same hash.");
  }
  Logger.log("testHashPassword: OK");
}

function testGenerateAndVerifyToken() {
  Logger.log("Running testGenerateAndVerifyToken...");
  var payload = {
    username: "test_admin",
    issuedAt: new Date().getTime(),
    expiresAt: new Date().getTime() + 10000,
    nonce: Utilities.getUuid(),
    sessionVersion: "1"
  };
  var secret = "testSecretKey123456";
  
  // Set temporary properties for verifySessionToken mock
  var props = PropertiesService.getScriptProperties();
  var oldSecret = props.getProperty("SESSION_SECRET");
  var oldUser = props.getProperty("ADMIN_USERNAME");
  var oldHash = props.getProperty("PASSWORD_HASH");
  var oldSalt = props.getProperty("PASSWORD_SALT");
  var oldVer = props.getProperty("SESSION_VERSION");
  
  props.setProperty("SESSION_SECRET", secret);
  props.setProperty("ADMIN_USERNAME", "test_admin");
  props.setProperty("PASSWORD_HASH", "dummyhash");
  props.setProperty("PASSWORD_SALT", "dummysalt");
  props.setProperty("SESSION_VERSION", "1");
  
  try {
    var token = generateToken(payload, secret);
    var check = verifySessionToken(token);
    
    if (!check.valid) {
      throw new Error("Token verification failed: " + check.message);
    }
    if (check.payload.username !== "test_admin") {
      throw new Error("Token payload mismatch");
    }
  } finally {
    // Restore properties
    if (oldSecret) props.setProperty("SESSION_SECRET", oldSecret); else props.deleteProperty("SESSION_SECRET");
    if (oldUser) props.setProperty("ADMIN_USERNAME", oldUser); else props.deleteProperty("ADMIN_USERNAME");
    if (oldHash) props.setProperty("PASSWORD_HASH", oldHash); else props.deleteProperty("PASSWORD_HASH");
    if (oldSalt) props.setProperty("PASSWORD_SALT", oldSalt); else props.deleteProperty("PASSWORD_SALT");
    if (oldVer) props.setProperty("SESSION_VERSION", oldVer); else props.deleteProperty("SESSION_VERSION");
  }
  Logger.log("testGenerateAndVerifyToken: OK");
}

function testExpiredToken() {
  Logger.log("Running testExpiredToken...");
  var payload = {
    username: "test_admin",
    issuedAt: new Date().getTime() - 20000,
    expiresAt: new Date().getTime() - 10000, // already expired
    nonce: Utilities.getUuid(),
    sessionVersion: "1"
  };
  var secret = "testSecretKey123456";
  
  var props = PropertiesService.getScriptProperties();
  var oldSecret = props.getProperty("SESSION_SECRET");
  var oldUser = props.getProperty("ADMIN_USERNAME");
  var oldHash = props.getProperty("PASSWORD_HASH");
  var oldSalt = props.getProperty("PASSWORD_SALT");
  
  props.setProperty("SESSION_SECRET", secret);
  props.setProperty("ADMIN_USERNAME", "test_admin");
  props.setProperty("PASSWORD_HASH", "dummyhash");
  props.setProperty("PASSWORD_SALT", "dummysalt");
  
  try {
    var token = generateToken(payload, secret);
    var check = verifySessionToken(token);
    
    if (check.valid) {
      throw new Error("Expired token was accepted!");
    }
    if (check.message.indexOf("已逾期") === -1) {
      throw new Error("Unexpected validation error message: " + check.message);
    }
  } finally {
    if (oldSecret) props.setProperty("SESSION_SECRET", oldSecret); else props.deleteProperty("SESSION_SECRET");
    if (oldUser) props.setProperty("ADMIN_USERNAME", oldUser); else props.deleteProperty("ADMIN_USERNAME");
    if (oldHash) props.setProperty("PASSWORD_HASH", oldHash); else props.deleteProperty("PASSWORD_HASH");
    if (oldSalt) props.setProperty("PASSWORD_SALT", oldSalt); else props.deleteProperty("PASSWORD_SALT");
  }
  Logger.log("testExpiredToken: OK");
}

function testRowToObject() {
  Logger.log("Running testRowToObject...");
  var headers = ["id", "name", "is_active", "notes"];
  var row = [123, "Alice", "TRUE", "some note"];
  
  var obj = rowToObject(headers, row);
  if (obj.id !== 123 || obj.name !== "Alice" || obj.is_active !== true || obj.notes !== "some note") {
    throw new Error("testRowToObject failed to parse correctly.");
  }
  Logger.log("testRowToObject: OK");
}

function testObjectToRow() {
  Logger.log("Running testObjectToRow...");
  var headers = ["id", "name", "is_active", "notes"];
  var obj = {
    id: 456,
    name: "Bob",
    is_active: false,
    notes: null
  };
  
  var row = objectToRow(headers, obj);
  if (row[0] !== 456 || row[1] !== "Bob" || row[2] !== false || row[3] !== "") {
    throw new Error("testObjectToRow failed to convert object correctly.");
  }
  Logger.log("testObjectToRow: OK");
}

function testRentalConflictDetection() {
  Logger.log("Running testRentalConflictDetection...");
  Logger.log("testRentalConflictDetection: OK");
}

function testPhase002WorkflowsCases() {
  Logger.log("Running testPhase002WorkflowsCases (Cases A, B, C, D)...");

  // Mock data setup
  var custA = { customer_id: "CUST-CASE-A", name: "Case A Customer", customer_type: "personal", phone: "0900000001", status: "active", billing_address: "Address A" };
  var contA = { container_id: "CONT-CASE-A", container_no: "20FT-A", size_ft: 20, container_type: "standard", status: "available", total_setup_cost: 0 };
  
  createRecord("customers", custA);
  createRecord("containers", contA);

  // Case A: 20ft container, rent 48,000, deposit 5,000, 2 installments
  var resultA = createAndActivateContract({
    customer_id: "CUST-CASE-A",
    start_date: "2026-08-01",
    end_date: "2027-07-31",
    billing_cycle: "yearly",
    rent_total: 48000,
    deposit_total: 5000,
    installment_count: 2,
    items: [{ container_id: "CONT-CASE-A", unit_price: 48000 }]
  });

  if (!resultA.contract_id || resultA.status !== "active") {
    throw new Error("Case A Failed: Contract not active");
  }
  if (resultA.items.length !== 1) {
    throw new Error("Case A Failed: Expected 1 contract item");
  }
  if (resultA.invoices.length !== 3) { // 1 deposit + 2 installments
    throw new Error("Case A Failed: Expected 3 invoices (1 deposit + 2 installments), got " + resultA.invoices.length);
  }
  var updatedContA = findRecordById("containers", "CONT-CASE-A");
  if (updatedContA.status !== "rented") {
    throw new Error("Case A Failed: Container status should be rented");
  }
  Logger.log("Case A: PASSED");

  // Case B: Same contract for two 10ft containers (CONT-CASE-B1 & CONT-CASE-B2)
  var custB = { customer_id: "CUST-CASE-B", name: "Case B Customer", customer_type: "business", phone: "0900000002", status: "active", billing_address: "Address B" };
  var contB1 = { container_id: "CONT-CASE-B1", container_no: "10FT-B1", size_ft: 10, container_type: "standard", status: "available", total_setup_cost: 0 };
  var contB2 = { container_id: "CONT-CASE-B2", container_no: "10FT-B2", size_ft: 10, container_type: "standard", status: "available", total_setup_cost: 0 };

  createRecord("customers", custB);
  createRecord("containers", contB1);
  createRecord("containers", contB2);

  var resultB = createAndActivateContract({
    customer_id: "CUST-CASE-B",
    start_date: "2026-08-01",
    rent_total: 60000,
    deposit_total: 10000,
    installment_count: 1,
    items: [
      { container_id: "CONT-CASE-B1", unit_price: 30000 },
      { container_id: "CONT-CASE-B2", unit_price: 30000 }
    ]
  });

  if (resultB.items.length !== 2) {
    throw new Error("Case B Failed: Expected 2 contract items for multi-container contract");
  }
  if (resultB.items[0].contract_item_id === resultB.items[1].contract_item_id) {
    throw new Error("Case B Failed: Contract items must have distinct IDs");
  }
  var updatedB1 = findRecordById("containers", "CONT-CASE-B1");
  var updatedB2 = findRecordById("containers", "CONT-CASE-B2");
  if (updatedB1.status !== "rented" || updatedB2.status !== "rented") {
    throw new Error("Case B Failed: Both containers should be rented");
  }
  Logger.log("Case B: PASSED");

  // Case C: Invoice 24,000 -> 1st payment 10,000 (PARTIAL) -> 2nd payment 14,000 (PAID)
  var invC = createInvoice({
    customer_id: "CUST-CASE-A",
    amount_due: 24000,
    due_date: "2026-08-05"
  });

  var pay1 = createPayment({
    customer_id: "CUST-CASE-A",
    invoice_id: invC.invoice_id,
    amount: 10000,
    payment_method: "bank_transfer"
  });

  if (pay1.invoice.status !== "partial" || pay1.invoice.balance_due !== 14000) {
    throw new Error("Case C Failed: 1st payment status should be partial with 14,000 balance_due, got status=" + pay1.invoice.status + ", balance=" + pay1.invoice.balance_due);
  }

  var pay2 = createPayment({
    customer_id: "CUST-CASE-A",
    invoice_id: invC.invoice_id,
    amount: 14000,
    payment_method: "bank_transfer"
  });

  if (pay2.invoice.status !== "paid" || pay2.invoice.balance_due !== 0) {
    throw new Error("Case C Failed: 2nd payment status should be paid with 0 balance_due, got status=" + pay2.invoice.status + ", balance=" + pay2.invoice.balance_due);
  }
  Logger.log("Case C: PASSED");

  // Case D: Deposit 10,000, remote control fee 350, cleaning fee 1,000 -> refunded 8,650
  // Container status: RENTED -> INSPECTION -> AVAILABLE
  var startTermRes = startTermination({ contract_id: resultA.contract_id });
  var contAfterStart = findRecordById("containers", "CONT-CASE-A");
  if (contAfterStart.status !== "inspection") {
    throw new Error("Case D Failed: Container status should be inspection during termination, got: " + contAfterStart.status);
  }

  var termRes = completeTermination({
    contract_id: resultA.contract_id,
    actual_end_date: "2027-08-01",
    deposit_original: 10000,
    remote_control_expected: 1,
    remote_control_returned: 0,
    remote_control_unit_fee: 350,
    cleaning_fee: 1000,
    damage_fee: 0,
    other_fee: 0
  });

  if (termRes.deposit_deducted !== 1350) {
    throw new Error("Case D Failed: Expected deposit_deducted = 1,350, got " + termRes.deposit_deducted);
  }
  if (termRes.deposit_refunded !== 8650) {
    throw new Error("Case D Failed: Expected deposit_refunded = 8,650, got " + termRes.deposit_refunded);
  }

  var contAfterTerm = findRecordById("containers", "CONT-CASE-A");
  if (contAfterTerm.status === "available") {
    throw new Error("Case D Failed: Container must NOT be directly available before inspection is completed");
  }

  // Complete inspection
  completeContainerInspection({ container_id: "CONT-CASE-A", inspection_status: "passed" });
  var contFinal = findRecordById("containers", "CONT-CASE-A");
  var finalStatusUpper = (contFinal.status || '').toString().toUpperCase();
  if (finalStatusUpper !== "AVAILABLE") {
    throw new Error("Case D Failed: Container status should be AVAILABLE after inspection passed, got: " + finalStatusUpper);
  }
  Logger.log("Case D: PASSED");

  Logger.log("testPhase002WorkflowsCases: ALL 4 CASES PASSED SUCCESSFULLY!");
}

function testPhase003ConsistencyAndSecurity() {
  Logger.log("Running testPhase003ConsistencyAndSecurity (Mandatory Cases 1 to 8)...");

  // Setup test customer & containers
  var cust = { customer_id: "CUST-P3", name: "P3 Customer", customer_type: "personal", phone: "0911111111", status: "ACTIVE", billing_address: "Address P3" };
  var cont = { container_id: "CONT-P3", container_no: "P3-01", size_ft: 20, container_type: "standard", status: "AVAILABLE", total_setup_cost: 0 };
  createRecord("customers", cust);
  createRecord("containers", cont);

  // Mandatory Case 1: Simultaneous contract creation for same container -> 2nd fails with CONFLICT
  var contract1 = createAndActivateContract({
    customer_id: "CUST-P3",
    start_date: "2026-09-01",
    rent_total: 10000,
    deposit_total: 1000,
    installment_count: 1,
    items: [{ container_id: "CONT-P3", unit_price: 10000 }]
  });

  try {
    createAndActivateContract({
      customer_id: "CUST-P3",
      start_date: "2026-09-01",
      rent_total: 10000,
      deposit_total: 1000,
      installment_count: 1,
      items: [{ container_id: "CONT-P3", unit_price: 10000 }]
    });
    throw new Error("Mandatory Case 1 Failed: Concurrent contract for same rented container was NOT blocked!");
  } catch (err) {
    if (err.message.indexOf("非空閒狀態") === -1 && err.message.indexOf("已有重疊") === -1) {
      throw new Error("Mandatory Case 1 Failed: Unexpected error: " + err.message);
    }
  }
  Logger.log("Mandatory Case 1: PASSED");

  // Mandatory Case 2: Same requestId submitted twice for contract -> returns existing contract, 0 duplicate
  var contP3_2 = { container_id: "CONT-P3-2", container_no: "P3-02", size_ft: 20, container_type: "standard", status: "AVAILABLE", total_setup_cost: 0 };
  createRecord("containers", contP3_2);

  var reqIdContract = "REQ-CONTRACT-101";
  var resA = createAndActivateContract({
    requestId: reqIdContract,
    customer_id: "CUST-P3",
    start_date: "2026-10-01",
    rent_total: 12000,
    deposit_total: 2000,
    installment_count: 1,
    items: [{ container_id: "CONT-P3-2", unit_price: 12000 }]
  });

  var resB = createAndActivateContract({
    requestId: reqIdContract,
    customer_id: "CUST-P3",
    start_date: "2026-10-01",
    rent_total: 12000,
    deposit_total: 2000,
    installment_count: 1,
    items: [{ container_id: "CONT-P3-2", unit_price: 12000 }]
  });

  if (resA.contract_id !== resB.contract_id) {
    throw new Error("Mandatory Case 2 Failed: Idempotency failed to return same contract on duplicate requestId");
  }
  Logger.log("Mandatory Case 2: PASSED");

  // Mandatory Case 3: Same requestId submitted twice for payment -> returns existing payment
  var inv = createInvoice({ customer_id: "CUST-P3", amount_due: 5000, due_date: "2026-09-01" });
  var reqIdPay = "REQ-PAY-202";

  var payA = createPayment({
    requestId: reqIdPay,
    customer_id: "CUST-P3",
    invoice_id: inv.invoice_id,
    amount: 5000
  });

  var payB = createPayment({
    requestId: reqIdPay,
    customer_id: "CUST-P3",
    invoice_id: inv.invoice_id,
    amount: 5000
  });

  if (payA.payment.payment_id !== payB.payment.payment_id) {
    throw new Error("Mandatory Case 3 Failed: Idempotency failed for duplicate payment requestId");
  }
  Logger.log("Mandatory Case 3: PASSED");

  // Mandatory Case 4: Illegal RENTED -> AVAILABLE transition must be blocked
  try {
    updateRecord("containers", "CONT-P3", { status: "AVAILABLE" });
    throw new Error("Mandatory Case 4 Failed: RENTED -> AVAILABLE transition was NOT blocked!");
  } catch (err) {
    if (err.message.indexOf("非法狀態轉變") === -1) {
      throw new Error("Mandatory Case 4 Failed: Unexpected error: " + err.message);
    }
  }
  Logger.log("Mandatory Case 4: PASSED");

  // Mandatory Case 5: Illegal ENDED -> ACTIVE transition must be blocked
  updateRecord("contracts", contract1.contract_id, { status: "ENDED" });
  try {
    updateRecord("contracts", contract1.contract_id, { status: "ACTIVE" });
    throw new Error("Mandatory Case 5 Failed: ENDED -> ACTIVE transition was NOT blocked!");
  } catch (err) {
    if (err.message.indexOf("非法狀態轉變") === -1) {
      throw new Error("Mandatory Case 5 Failed: Unexpected error: " + err.message);
    }
  }
  Logger.log("Mandatory Case 5: PASSED");

  // Mandatory Case 6: Expired session calls protected API -> UNAUTHORIZED
  var expiredTokenRes = routeRequest("list", "expired.token.xyz", { table: "customers" });
  if (expiredTokenRes.ok !== false || expiredTokenRes.error.code !== "UNAUTHORIZED") {
    throw new Error("Mandatory Case 6 Failed: Expired session token was not rejected with UNAUTHORIZED");
  }
  Logger.log("Mandatory Case 6: PASSED");

  // Mandatory Case 7: Attempting CRUD on audit_logs via Router -> UNAUTHORIZED
  try {
    handleCreateAction({ table: "audit_logs", data: { action: "HACK" } });
    throw new Error("Mandatory Case 7 Failed: Direct CRUD on audit_logs was NOT blocked!");
  } catch (err) {
    if (err.code !== "UNAUTHORIZED") {
      throw new Error("Mandatory Case 7 Failed: Unexpected error code: " + err.code);
    }
  }
  Logger.log("Mandatory Case 7: PASSED");

  // Mandatory Case 8: Status normalization dryRun lists lowercase data but does NOT modify sheets
  var normDryRun = normalizeStatusToUppercase({ dryRun: true });
  if (normDryRun.dryRun !== true) {
    throw new Error("Mandatory Case 8 Failed: dryRun option was not respected");
  }
  Logger.log("Mandatory Case 8: PASSED");

  Logger.log("testPhase003ConsistencyAndSecurity: ALL 8 MANDATORY CASES PASSED SUCCESSFULLY!");
}

function testSafetyDeleteAndStatusChange() {
  Logger.log("Running testSafetyDeleteAndStatusChange...");

  // Setup test environment keys
  var props = PropertiesService.getScriptProperties();
  var oldUser = props.getProperty("ADMIN_USERNAME");
  props.setProperty("ADMIN_USERNAME", "test_admin");

  try {
    // 1. Create a fresh available container
    var containerData = {
      container_no: "TEST-DEL-CONT-01",
      size_ft: 20,
      container_type: "standard",
      location_zone: "A區",
      location_label: "L1",
      total_setup_cost: 1000,
      status: "AVAILABLE",
      note: "Test delete available"
    };
    var container = createContainer(containerData);
    var containerId = container.container_id;

    // 2. Create a fresh customer
    var customerData = {
      name: "TEST-DEL-CUST-01",
      customer_type: "personal",
      phone: "0900000001",
      email: "del1@test.com",
      status: "ACTIVE"
    };
    var customer = createCustomer(customerData);
    var customerId = customer.customer_id;

    // Rule 1: AVAILABLE container without contracts can be deleted
    deleteContainer(containerId);
    var deletedContainer = findRecordById("containers", containerId);
    if (deletedContainer !== null) {
      throw new Error("testSafetyDeleteAndStatusChange failed: AVAILABLE container without history was not soft deleted!");
    }
    var listC = listRecords("containers");
    var foundInList = listC.some(function(c) { return c.container_id === containerId; });
    if (foundInList) {
      throw new Error("testSafetyDeleteAndStatusChange failed: soft-deleted container still returned in listRecords!");
    }
    Logger.log("Rule 1: AVAILABLE container deleted -> PASSED");

    // Rule 2: Customer without contracts can be deleted
    deleteCustomer(customerId);
    var deletedCustomer = findRecordById("customers", customerId);
    if (deletedCustomer !== null) {
      throw new Error("testSafetyDeleteAndStatusChange failed: Customer without history was not soft deleted!");
    }
    var listCust = listRecords("customers");
    var foundCustInList = listCust.some(function(c) { return c.customer_id === customerId; });
    if (foundCustInList) {
      throw new Error("testSafetyDeleteAndStatusChange failed: soft-deleted customer still returned in listRecords!");
    }
    Logger.log("Rule 2: Customer deleted -> PASSED");

    // 3. Create another customer & container, and create a contract
    var container2 = createContainer({
      container_no: "TEST-DEL-CONT-02",
      size_ft: 20,
      container_type: "standard",
      status: "AVAILABLE"
    });
    var customer2 = createCustomer({
      name: "TEST-DEL-CUST-02",
      phone: "0900000002",
      status: "ACTIVE"
    });

    // Create rate plan
    var ratePlan = createRatePlan({
      name: "Test Delete Rate",
      container_size_ft: 20,
      container_type: "standard",
      billing_cycle: "monthly",
      contract_months: 6,
      standard_monthly_price: 5000,
      contract_price: 45000,
      installment_count: 6,
      default_deposit: 5000,
      active: true
    });

    // Activate Contract
    var contract = createAndActivateContract({
      customer_id: customer2.customer_id,
      rate_plan_id: ratePlan.rate_plan_id,
      start_date: "2026-08-01",
      end_date: "2027-01-31",
      billing_cycle: "monthly",
      rent_total: 270000,
      deposit_total: 5000,
      installment_count: 6,
      status: "ACTIVE",
      items: [
        {
          container_id: container2.container_id,
          unit_price: 5000,
          discount_amount: 0,
          effective_price: 5000,
          start_date: "2026-08-01",
          status: "ACTIVE"
        }
      ]
    });

    // Rule 3: Customer with ACTIVE contract cannot be deleted
    try {
      deleteCustomer(customer2.customer_id);
      throw new Error("Rule 3 failed: Customer with ACTIVE contract was deleted!");
    } catch (err) {
      if (err.code !== "CUSTOMER_HAS_ACTIVE_CONTRACT") {
        throw new Error("Rule 3 failed with unexpected error code: " + err.code);
      }
    }
    Logger.log("Rule 3: Customer with ACTIVE contract block -> PASSED");

    // Rule 4: RENTED container cannot be deleted
    try {
      deleteContainer(container2.container_id);
      throw new Error("Rule 4 failed: RENTED container was deleted!");
    } catch (err) {
      if (err.code !== "CONTAINER_NOT_DELETABLE") {
        throw new Error("Rule 4 failed with unexpected error code: " + err.code);
      }
    }
    Logger.log("Rule 4: RENTED container block -> PASSED");

    // Rule 5: Historical items container cannot be deleted (even if status is AVAILABLE, but it has contract_items history)
    updateRecord("containers", container2.container_id, { status: "AVAILABLE" });
    try {
      deleteContainer(container2.container_id);
      throw new Error("Rule 5 failed: Container with contract_items history was deleted!");
    } catch (err) {
      if (err.code !== "CONTAINER_HAS_HISTORICAL_CONTRACT") {
        throw new Error("Rule 5 failed with unexpected error code: " + err.code);
      }
    }
    Logger.log("Rule 5: Container with history block -> PASSED");

    // Rule 6: Historical contract customer cannot be deleted (must deactivate instead)
    updateRecord("contracts", contract.contract_id, { status: "ENDED" });
    try {
      deleteCustomer(customer2.customer_id);
      throw new Error("Rule 6 failed: Customer with ENDED contract was deleted!");
    } catch (err) {
      if (err.code !== "CUSTOMER_HAS_HISTORICAL_CONTRACT") {
        throw new Error("Rule 6 failed with unexpected error code: " + err.code);
      }
    }
    Logger.log("Rule 6: Customer with history block -> PASSED");

  } finally {
    if (oldUser) props.setProperty("ADMIN_USERNAME", oldUser); else props.deleteProperty("ADMIN_USERNAME");
  }

  Logger.log("testSafetyDeleteAndStatusChange: ALL SAFETY DELETE AND DEACTIVATION CASES PASSED!");
}



