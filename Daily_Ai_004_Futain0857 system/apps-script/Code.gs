/**
 * Main Web App POST entry point
 */
function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return makeJsonOutput({
        ok: false,
        data: null,
        error: {
          code: "BAD_REQUEST",
          message: "請求內容不可為空"
        }
      });
    }

    // Parse payload
    var rawContents = e.postData.contents;
    var requestData;
    try {
      requestData = JSON.parse(rawContents);
    } catch (parseError) {
      return makeJsonOutput({
        ok: false,
        data: null,
        error: {
          code: "INVALID_JSON",
          message: "無法解析 JSON 格式的請求內容"
        }
      });
    }

    var action = requestData.action;
    var sessionToken = requestData.sessionToken;
    var payload = requestData.payload || {};

    if (!action) {
      return makeJsonOutput({
        ok: false,
        data: null,
        error: {
          code: "MISSING_ACTION",
          message: "缺少 action 參數"
        }
      });
    }

    // Dispatch request
    var responseData = routeRequest(action, sessionToken, payload);
    return makeJsonOutput(responseData);

  } catch (globalError) {
    return makeJsonOutput({
      ok: false,
      data: null,
      error: {
        code: "INTERNAL_SERVER_ERROR",
        message: "伺服器內部錯誤: " + globalError.toString()
      }
    });
  }
}

/**
 * Helper to generate JSON output with CORS options (CORS is native to GAS Web Apps, but we format output)
 */
function makeJsonOutput(responseObj) {
  return ContentService.createTextOutput(JSON.stringify(responseObj))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * OPTIONS request handler (for CORS preflight)
 */
function doOptions(e) {
  return ContentService.createTextOutput("")
    .setMimeType(ContentService.MimeType.TEXT);
}
