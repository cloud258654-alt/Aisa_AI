// Preload script to inject global.crypto in Node.js < 20 (CommonJS format)
try {
  if (!global.crypto) {
    global.crypto = require('node:crypto');
  }
} catch (e) {
  console.error("Failed to inject global.crypto:", e);
}
