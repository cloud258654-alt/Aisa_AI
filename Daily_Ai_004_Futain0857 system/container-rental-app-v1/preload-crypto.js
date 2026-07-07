// Preload script to inject global.crypto in Node.js < 20
// This is required to make serialize-javascript (used by rollup-plugin-terser / workbox) compile on Node 18.
try {
  if (!global.crypto) {
    global.crypto = require('node:crypto');
  }
} catch (e) {
  console.error("Failed to inject global.crypto:", e);
}
