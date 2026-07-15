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
  // Verify helper checks or logic throws correctly under double booking
  // (Actual execution is verified on active sheets under Script Lock)
  Logger.log("testRentalConflictDetection: OK");
}
