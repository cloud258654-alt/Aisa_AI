/**
 * Handle authentication and session token verification
 */

/**
 * Handle login request
 */
function handleLoginAction(payload) {
  var username = payload.username;
  var password = payload.password;

  if (!username || !password) {
    return {
      ok: false,
      data: null,
      error: {
        code: "INVALID_CREDENTIALS",
        message: "帳號或密碼錯誤"
      }
    };
  }

  var props = PropertiesService.getScriptProperties().getProperties();
  var expectedUsername = props.ADMIN_USERNAME || "admin";
  var expectedHash = props.PASSWORD_HASH;
  var expectedSalt = props.PASSWORD_SALT;

  if (!expectedHash) {
    return {
      ok: false,
      data: null,
      error: {
        code: "SYSTEM_NOT_CONFIGURED",
        message: "系統尚未初始化管理員密碼，請聯絡系統管理員"
      }
    };
  }

  // Lockout verification
  var cache = CacheService.getScriptCache();
  var lockKey = "login_lock_" + username;
  var countKey = "login_fail_count_" + username;
  
  var isLocked = cache.get(lockKey);
  if (isLocked) {
    return {
      ok: false,
      data: null,
      error: {
        code: "LOCKED_OUT",
        message: "連續登入失敗次數過多，請於 5 分鐘後再試"
      }
    };
  }

  // Verify username and password
  var inputHash = hashPassword(password, expectedSalt);
  
  // Constant-time string comparison to mitigate timing attacks
  var authSuccess = (username === expectedUsername) && safeCompare(inputHash, expectedHash);

  if (!authSuccess) {
    // Record failure
    var failures = parseInt(cache.get(countKey) || "0", 10) + 1;
    var maxFailures = parseInt(props.LOGIN_MAX_FAILURES || "5", 10);
    var lockMinutes = parseInt(props.LOGIN_LOCK_MINUTES || "5", 10);

    if (failures >= maxFailures) {
      cache.put(lockKey, "1", lockMinutes * 60);
      cache.remove(countKey);
      return {
        ok: false,
        data: null,
        error: {
          code: "LOCKED_OUT",
          message: "連續登入失敗次數過多，請於 " + lockMinutes + " 分鐘後再試"
        }
      };
    } else {
      cache.put(countKey, failures.toString(), 300); // Failures expire in 5 minutes
      return {
        ok: false,
        data: null,
        error: {
          code: "INVALID_CREDENTIALS",
          message: "帳號或密碼錯誤"
        }
      };
    }
  }

  // Clear failures on success
  cache.remove(countKey);
  cache.remove(lockKey);

  // Generate Token
  var ttlSeconds = parseInt(props.SESSION_TTL_SECONDS || "86400", 10); // Default 1 day
  var expiresAt = new Date().getTime() + (ttlSeconds * 1000);
  
  var sessionPayload = {
    username: username,
    expiresAt: expiresAt,
    salt: Math.random().toString()
  };
  
  var token = generateToken(sessionPayload, props.SESSION_SECRET || "default_session_secret");

  return {
    ok: true,
    data: {
      sessionToken: token,
      expiresAt: new Date(expiresAt).toISOString()
    },
    error: null
  };
}

/**
 * Handle logout request
 */
function handleLogoutAction(sessionToken) {
  // Since tokens are stateless and verified by signature, we can't easily revoke them
  // without storing a blacklist. For a single admin app, clearing token in frontend sessionStorage
  // is sufficient. If needed, a blocklist could be stored in CacheService.
  var cache = CacheService.getScriptCache();
  cache.put("blacklisted_" + sessionToken, "1", 86400); // blocklist for 24h
  return { ok: true, data: { success: true }, error: null };
}

/**
 * Verify Session Token
 */
function verifySessionToken(token) {
  if (!token) return { valid: false, message: "缺少驗證 Token" };

  var cache = CacheService.getScriptCache();
  if (cache.get("blacklisted_" + token)) {
    return { valid: false, message: "此 Token 已登出失效" };
  }

  var parts = token.split(".");
  if (parts.length !== 2) return { valid: false, message: "Token 格式無效" };

  var payloadBase64 = parts[0];
  var signatureBase64 = parts[1];

  var props = PropertiesService.getScriptProperties().getProperties();
  var secret = props.SESSION_SECRET || "default_session_secret";

  // Verify Signature
  var expectedSignatureBytes = Utilities.computeHmacSha256Signature(payloadBase64, secret);
  var expectedSignatureBase64 = Utilities.base64EncodeWebSafe(expectedSignatureBytes);

  if (!safeCompare(signatureBase64, expectedSignatureBase64)) {
    return { valid: false, message: "驗證簽章失敗" };
  }

  // Decode Payload
  var payloadStr = Utilities.newBlob(Utilities.base64DecodeWebSafe(payloadBase64)).getDataAsString();
  var payload;
  try {
    payload = JSON.parse(payloadStr);
  } catch (e) {
    return { valid: false, message: "無法解析 Token 內容" };
  }

  // Check Expiration
  var now = new Date().getTime();
  if (now > payload.expiresAt) {
    return { valid: false, message: "驗證已逾期，請重新登入" };
  }

  return { valid: true, payload: payload };
}

/**
 * Generate Signed Token
 */
function generateToken(payload, secret) {
  var payloadStr = JSON.stringify(payload);
  var payloadBase64 = Utilities.base64EncodeWebSafe(Utilities.newBlob(payloadStr).getBytes());
  
  var signatureBytes = Utilities.computeHmacSha256Signature(payloadBase64, secret);
  var signatureBase64 = Utilities.base64EncodeWebSafe(signatureBytes);
  
  return payloadBase64 + "." + signatureBase64;
}

/**
 * Hash password with SHA-256 and Salt
 */
function hashPassword(password, salt) {
  var rawValue = password + salt;
  var digest = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, rawValue, Utilities.Charset.UTF_8);
  
  // Convert bytes to hex string
  var hexString = "";
  for (var i = 0; i < digest.length; i++) {
    var byteVal = digest[i];
    if (byteVal < 0) byteVal += 256;
    var byteHex = byteVal.toString(16);
    if (byteHex.length == 1) byteHex = "0" + byteHex;
    hexString += byteHex;
  }
  return hexString;
}

/**
 * Constant-time string comparison to prevent timing attacks
 */
function safeCompare(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string') return false;
  if (a.length !== b.length) return false;
  var result = 0;
  for (var i = 0; i < a.length; i++) {
    result |= (a.charCodeAt(i) ^ b.charCodeAt(i));
  }
  return result === 0;
}
