# 福田貨櫃倉儲出租系統 — 正式與測試環境部署手冊 (DEPLOYMENT.md)

- **更新日期**：2026-07-22
- **版本**：v1.0.0
- **系統架構**：React Vite PWA + Google Apps Script Web App + Google Sheets

---

## 🏢 一、環境隔離架構

本系統嚴格區分 **TEST 測試環境** 與 **PRODUCTION 正式環境**，兩者完全獨立，嚴禁共用 Google Spreadsheet 或 Secret。

```text
[ 前端 React PWA ] 
   │
   ├─► TEST 環境 (.env.test) ──────► GAS Test Web App ─────► TEST Google Sheet
   │
   └─► PRODUCTION 環境 (.env.prod) ──► GAS Prod Web App ────► PROD Google Sheet
```

---

## 🛠️ 二、後端 (GAS) 部署 SOP

### 步驟 1：建立試算表與設定 Script Properties
1. 開啟 Google Sheets，建立一空白試算表，命名為 `福田貨櫃倉儲出租系統_PRODUCTION`。
2. 複製網址中之 Spreadsheet ID (例如 `1A2b3C4d5E...`)。
3. 開啟 Apps Script 專案，進入「專案設定 ➔ 指令碼屬性 (Script Properties)」，新增下列 6 個設定：

```text
SPREADSHEET_ID = [您的 Spreadsheet ID]
ADMIN_USERNAME = admin
PASSWORD_SALT = [隨機 Salt 字串]
PASSWORD_HASH = [SHA-256 密碼雜湊]
SESSION_SECRET = [隨機強密鑰]
SESSION_TTL_SECONDS = 86400
```

### 步驟 2：初始化試算表與白名單校驗
1. 在 GAS 編輯器中選擇 `Setup.gs`，執行 `setupSpreadsheet()` 函式，自動建立 14 張工作表與欄位標題。
2. 選擇 `ManualTests.gs`，執行 `testPhase003ConsistencyAndSecurity()` 確保 8 項安全與狀態機測試 PASS。

### 步驟 3：發布 Web 應用程式 (Web App)
1. 點選右上方「部署 ➔ 新增部署」。
2. 種類選擇「Web 應用程式」。
3. 設定：
   - 說明：`v1.0.0 正式上線部署`
   - 執行身份：`我 (USER_DEPLOYING)`
   - 誰可以存取：`所有人 (Anyone)` (此項為防止 CORS 與 302 轉向之關鍵)
4. 點選「部署」，並複製獲得的 `https://script.google.com/macros/s/DEPLOYMENT_ID/exec` 網址。

---

## 💻 三、前端 (React Vite PWA) 打包與託管 SOP

### 步驟 1：設定環境變數
在 `container-rental-app-v1/.env.local` 寫入 GAS Web App 部署網址：

```env
VITE_GAS_WEB_APP_URL=https://script.google.com/macros/s/DEPLOYMENT_ID/exec
```

### 步驟 2：執行自動化檢查與靜態打包
在終端機中執行：

```bash
cd "Daily_Ai_004_Futain0857 system/container-rental-app-v1"
npm ci
npm run lint
npm run test
npm run build
```

打包成功後，產出之 `dist/` 目錄即可部署至 GitHub Pages、Vercel 或 Cloudflare Pages 等靜態託管平台。
