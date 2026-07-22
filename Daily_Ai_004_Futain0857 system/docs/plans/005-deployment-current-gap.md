# 005 — 部署與端到端驗證現況盤點 (Deployment Current Gap Analysis)

- **盤點日期**：2026-07-22
- **對應計畫**：`docs/plans/005-deployment-e2e-modules-plans.md`
- **狀態**：`COMPLETED_GAP_ANALYSIS`

---

## 1. 現有 GAS 專案設定
- **原始碼目錄**：`apps-script/` (包含 `Code.gs`, `Router.gs`, `Auth.gs`, `StateMachine.gs`, `Idempotency.gs`, `Setup.gs`, `ManualTests.gs` 等 25 個 `.gs` / `.json` 檔案)。
- **進入點**：`doGet(e)` 與 `doPost(e)` 定義於 `Code.gs`。
- **權限與 Session**：採單一管理員模式，在後端依據 `ScriptProperties` 校驗 `ADMIN_USERNAME`, `PASSWORD_HASH`, `SESSION_SECRET` 與 HMAC Signed Token。

---

## 2. `.clasp.json` 與 `.clasp` 現況
- `.clasp.json` 現有內容範例：`{"scriptId":"YOUR_SCRIPT_ID_HERE","rootDir":"."}`
- `.clasp` 包含本機工具偏好配置。
- **GAP**：正式部署前，須透過 Clasp 登入 (`clasp login`) 並個別推播至 **TEST 測試腳本** 與 **PRODUCTION 正式腳本**。

---

## 3. `appsscript.json` 現況
- **時區與 Runtime**：`Asia/Taipei`, `V8` 引擎, `STACKDRIVER` 例外紀錄。
- **Web App 設定**：`access: "ANYONE"`, `executeAs: "USER_DEPLOYING"`。
- **狀態**：已符合正確認證與 CORS/iframe 跨域請求基礎。

---

## 4. Script Properties 需求清單
在每個 GAS 專案（TEST / PRODUCTION）的「專案設定 ➔ 指令碼屬性」中，必須包含以下 6 大變數：

| 變數名稱 | 範例與用途 | 是否可提交 Git |
| --- | --- | :---: |
| `SPREADSHEET_ID` | 綁定之 Google Sheets 試算表 ID | ❌ 嚴禁 |
| `ADMIN_USERNAME` | 管理員帳號 (預設如 `admin`) | ❌ 嚴禁 |
| `PASSWORD_SALT` | 密碼雜湊鹽值 (預設如 `futain_salt_2026`) | ❌ 嚴禁 |
| `PASSWORD_HASH` | SHA-256 雜湊密碼 | ❌ 嚴禁 |
| `SESSION_SECRET` | Session 簽章 Secret 密鑰 | ❌ 嚴禁 |
| `SESSION_TTL_SECONDS` | 會期有效秒數 (預設 `86400`) | ❌ 嚴禁 |

---

## 5. 現有 Google Sheets Schema (14 張工作表)
- **相容 Legacy 區塊 (3 張)**：`rental_records`, `customer_ledgers`, `management_ledgers` (嚴禁刪除或破壞結構)。
- **Phase 001-003 升級架構 (11 張)**：
  - 核心業務表：`containers`, `customers`, `rate_plans`, `contracts`, `contract_items`, `invoices`, `payments`, `termination_records`
  - 稽核與一致性表：`audit_logs`, `request_logs`, `session_logs`
- **初始化機制**：執行 `Setup.gs` 之 `setupSpreadsheet()` 自動補齊缺少的欄位標題與預設資料。

---

## 6. 前端環境變數與 Client 設定
- **現有檔案**：`container-rental-app-v1/.env.example`
- **正式 / 測試變數**：
  ```env
  VITE_GAS_WEB_APP_URL=https://script.google.com/macros/s/DEPLOYMENT_ID/exec
  ```
- **隔離規範**：本機開發使用 `.env.local`，正式與測試打包使用分開之 CI/Env 設定。

---

## 7. 現有部署平台與架構
- **後端**：Google Apps Script (Web App)
- **前端**：Vite React SPA + Progressive Web App (PWA) 靜態託管（如 GitHub Pages / Vercel / Cloudflare Pages / Nginx）

---

## 8. PWA Manifest 與 Service Worker 現況
- ** Manifest**：`container-rental-app-v1/vite.config.ts` 已整合 Vite PWA Plugin，定義 `manifest.webmanifest`（包含 `name: "福田貨櫃倉儲出租系統"`, `short_name: "福田貨櫃"`, `theme_color: "#021341"`）。
- **Service Worker**：產出 `dist/sw.js` 實現靜態資源離線快取與 PWA 安裝提示。
- **離線防呆**：當網路離線 (`!navigator.onLine`) 時，前端按鈕會彈出「⚠️ 目前離線，請恢復網路連線後再進行儲存/異動」明確提示，防範錯覺誤認。

---

## 9. 現有 CI Workflow 自動化
- `npm run lint`：ESLint 0 錯誤、0 警告。
- `npm run test`：Vitest 15/15 單元與核心營運流程測試通過。
- `npm run build`：`tsc -b && vite build` 成功建置。

---

## 10. 備份與復原現況 (BACKUP_RESTORE)
- **現況**：需建立獨立文件 `project_management/BACKUP_RESTORE.md`。
- **機制**：
  - 定期透過 Google Drive API 或自動化 Script 備份 `.xlsx / 試算表副本`。
  - Script Properties 集中備份於加密金鑰庫。
  - 還原防護：在 TEST 環境模擬還原演練。

---

## 11. TEST 與 PRODUCTION 尚缺少的項目
1. 建立兩套完全隔離的 Google Sheets（`TEST_SPREADSHEET` 與 `PRODUCTION_SPREADSHEET`）。
2. 部署兩套獨立 GAS Web App 獲得對應之 `TEST_EXEC_URL` 與 `PROD_EXEC_URL`。
3. 前端匯出 CSV 報表功能 (UTF-8 BOM 中文無亂碼，分開匯出租金、押金、付款、支出)。
4. 建立 `project_management/BACKUP_RESTORE.md` 與演練紀錄。
5. 更新 `docs/DEPLOYMENT.md` 與 `docs/TEST_REPORT.md`。

---

## 12. 需要人工操作的步驟
1. 在 Google Sheets 建立正式與測試試算表，複製 Spreadsheet ID。
2. 開啟對應 GAS 專案設定頁面，設定 6 大 Script Properties。
3. 執行 GAS `setupSpreadsheet()` 與 `testPhase003ConsistencyAndSecurity()`。
4. 在 GAS 介面進行「新增部署」➔ 選擇「Web 應用程式」➔ 設定存取權限為「所有人 (Anyone)」。
5. 將獲得的 `exec` 網址寫入前端環境變數建置。

---

## 13. 不得提交 Git 的敏感資訊清單
- `.env.local`
- `.clasp.json` (含有真實 `scriptId`)
- `.clasprc.json` (Clasp oauth 憑證)
- `ScriptProperties` 內的密碼 Hash、Salt、Session Secret、Spreadsheet ID
- 交付文件中的正式連線 Token 與客戶敏感個資

---

## 14. 部署風險及回復方案
- **風險 1：Web App 部署權限未設為 Anyone**
  - *現象*：前端呼叫回應 302 重定向至 Google Login 頁面或 CORS 阻擋。
  - *回復*：於 GAS 部署設定中確認「誰可以存取」已改為「所有人 (Anyone)」。
- **風險 2：試算表欄位缺失**
  - *現象*：後端讀寫報錯 `Column not found`。
  - *回復*：重新執行一次 `Setup.gs` 之 `setupSpreadsheet()` 自動擴充修復欄位。
- **風險 3：GAS 部署版本未更新**
  - *現象*：程式碼已更新但 Web App 仍運行舊版本。
  - *回復*：於 GAS 介面點選「管理部署」➔ 編輯 ➔ 選擇「新版本 (New version)」後儲存。
