/**
 * Common utilities and helper functions
 */

/**
 * Generate a unique ID (e.g. CUST-YYYYMMDD-XXXX)
 */
function generateUniqueId(prefix) {
  var now = new Date();
  var yyyy = now.getFullYear().toString();
  var mm = (now.getMonth() + 1).toString();
  if (mm.length === 1) mm = "0" + mm;
  var dd = now.getDate().toString();
  if (dd.length === 1) dd = "0" + dd;
  
  var dateStr = yyyy + mm + dd;
  
  // 4 random uppercase chars/numbers for unique check
  var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  var randomStr = '';
  for (var i = 0; i < 4; i++) {
    randomStr += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  
  return prefix + "-" + dateStr + "-" + randomStr;
}

/**
 * Get formatted local timestamp string
 */
function getIsoTimestamp() {
  return Utilities.formatDate(new Date(), "Asia/Taipei", "yyyy-MM-dd HH:mm:ss");
}

/**
 * Parse YYYY-MM-DD date string into a Date object (UTC safe or local safe)
 */
function parseDateString(str) {
  if (!str) return null;
  var parts = str.split(' ')[0].split('-');
  if (parts.length !== 3) return null;
  // Use local timezone to construct Date
  return new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10));
}

/**
 * Format a Date object to YYYY-MM-DD format
 */
function formatDateString(date) {
  if (!date || isNaN(date.getTime())) return '';
  var yyyy = date.getFullYear().toString();
  var mm = (date.getMonth() + 1).toString();
  if (mm.length === 1) mm = "0" + mm;
  var dd = date.getDate().toString();
  if (dd.length === 1) dd = "0" + dd;
  return yyyy + "-" + mm + "-" + dd;
}
