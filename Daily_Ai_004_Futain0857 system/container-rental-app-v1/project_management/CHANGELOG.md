# 貨櫃出租 App V1 - 專案異動紀錄 (Changelog)

本檔案記錄本專案各階段的開發里程碑與重大架構變更。

---

## [1.5.0] - 2026-07-21

### Added (新增)
- **資料一致性、安全與稽核強化 (Phase 003)**
  - 後端：狀態值正規化為大寫 Canonical Status (`AVAILABLE`, `RENTED`, `INSPECTION`, `MAINTENANCE`, `DRAFT`, `ACTIVE`, `ENDING`, `ENDED`, `UNPAID`, `PARTIAL`, `PAID`, `VOID`, `CONFIRMED`)，並新增 `StateMachine.gs` 白名單轉換校驗（非法轉換如 `RENTED -> AVAILABLE` 或 `ENDED -> ACTIVE` 自動被拒絕）。
  - 後端：新增 `Idempotency.gs` (`checkAndLockRequestId`, `updateRequestIdSuccess`, `updateRequestIdFailed`)，針對寫入 RequestId 提供 `PROCESSING`, `SUCCESS`, `FAILED` 狀態控制，防止重複請求。
  - 後端：所有寫入與跨表異動統一採用 `LockService.getScriptLock()` 於鎖內重讀最新狀態並執行 `SpreadsheetApp.flush()`。
  - 後端：`Router.gs` 加入對 `audit_logs` 資料表之一般 CRUD 的權限阻擋 (`UNAUTHORIZED`)。
  - 後端：`Migration.gs` 新增 `normalizeStatusToUppercase({ dryRun })`。
  - 前端：TypeScript 型別與 Zod Schema 定義大寫狀態 Union Types。
  - 測試：`ManualTests.gs` 新增 8 大必測安全與一致性案例。

---

## [1.4.0] - 2026-07-21

### Added (新增)
- **核心營運流程實作 (Phase 002)**
  - 後端：`ContractsService.gs` 新增單櫃/多櫃合約啟用 (`createAndActivateContract`) 與續約 (`renewContract`)，包含獨立 `contract_items` 建立與自動開立分期帳單。
  - 後端：`PaymentsService.gs` 與 `InvoicesService.gs` 支援多筆付款、部分付款 (`partial`) 狀態動態計算與作廢紀錄復原 (`voidPayment`)。
  - 後端：`TerminationService.gs` 實作退租啟動 (`startTermination`)、7 步驟押金費用結算 (`completeTermination`) 與貨櫃檢查狀態解鎖 (`completeContainerInspection`)，確保退租時貨櫃先進入 `inspection` 狀態而非直接改為 `available`。
  - 前端：新增 `ContractsPage.tsx`, `InvoicesPage.tsx`, `TerminationPage.tsx`, `RatePlansPage.tsx` 四大流程操作頁面與路由對應。
  - 測試：`ManualTests.gs` 與 Vitest (`tests/workflows.test.ts`) 補齊案例 A (單櫃與分期)、案例 B (多櫃同一合約)、案例 C (部分付款至結清)、案例 D (退租扣款與檢查狀態流轉) 之測試驗證。

---

## [1.3.0] - 2026-07-21

### Added (新增)
- **資料模型與 API 升級 (Phase 001)**
  - 後端：新增 `rate_plans`, `contracts`, `contract_items`, `invoices`, `payments`, `expenses`, `termination_records`, `request_logs` 資料表與對應的 `RatePlansService`, `ContractsService`, `InvoicesService`, `PaymentsService`, `TerminationService` 模組。
  - 後端：新增 `Migration.gs` 資料備份與 Dry-run 遷移腳本（`backupLegacySheets`, `migrateLegacyRentalsToContracts`, `migrateLegacyLedgersToInvoicesAndPayments`, `verifyMigration`）。
  - 前端：新增型別定義 (`ratePlan.ts`, `contract.ts`, `contractItem.ts`, `invoice.ts`, `payment.ts`, `terminationRecord.ts`)。
  - 前端：新增 API 模組並採用 Zod 進行 Response 通訊協議驗證 (`ratePlansApi.ts`, `contractsApi.ts`, `invoicesApi.ts`, `paymentsApi.ts`, `terminationsApi.ts`)。

### Changed (變更)
- `Setup.gs` 與 `SheetRepository.gs` 支援新版工作表及舊版工作表並存初始化。
- `Router.gs` 加入 Phase 001 實體路由與 `dryRunMigration`, `verifyMigration` 端點。
- `ManualTests.gs` 擴充 Phase 001 遷移測試案例。

---

## [1.2.0] - 2026-07-15

### Added (新增)
- **Google Apps Script 後端專案 (`apps-script/`)**
  - `Code.gs`：統一接收前端 POST text/plain JSON 請求。
  - `Router.gs`：進行 Action 邏輯分發與並行鎖定。
  - `Auth.gs`：實作管理員密碼比對（常數時間比對防止時序攻擊）與登入失敗鎖定（防禦暴力破解），簽章簽發與會期校驗。
  - `SheetRepository.gs`：實作試算表單列讀寫與物件轉換，處理軟刪除與 `audit_logs` 審計追蹤。
  - 各模組 Service：`CustomersService.gs`, `ContainersService.gs`, `RentalsService.gs`, `LedgersService.gs`, `DashboardService.gs` 及輸入 Zod-like 欄位驗證。
  - `Setup.gs`：支援初始化各分頁、表頭欄位凍結與格式化，不損毀既有資料。
- **前端 Web App Client**
  - `gasClient.ts`：專用 fetch 客戶端，支援自動跟隨 302 重導向並於 Token 到期時自動分發 Session 逾期事件。
  - `SessionContext.tsx` 與 `useSession.ts`：提供單一管理員會期狀態控管，Token 儲存於 `sessionStorage` 隨關閉分頁而清除。

### Changed (變更)
- **前端頁面營運接口**：將 Dashboard、客戶、貨櫃、合約、客戶流水及場地支出頁面全面改接至 GAS client API，取消 Firestore 的呼叫。
- **離線機制重構**：變更為**線上優先**模式，若瀏覽器離線（斷網），畫面上方顯示警告橫幅，並將「新增、編輯、登記收款、辦理退租」等變更按鈕轉為禁用狀態，只開放離線唯讀以防資料冲突。
- **CI / CD 與單元測試**：
  - `.github/workflows/container-rental-ci.yml` 移除了對 Firebase Emulators 的依賴，加入 Apps Script 檔案結構存在性檢查以及防止密碼/試算表 ID 洩露的靜態 grep 掃描。
  - `package.json` 腳本中廢除 rules 測試。
  - 增設 `tests/gasApiAndSession.test.ts` 以測試計算邏輯與 GAS 串接錯誤分支。

### Removed (移除)
- 刪除或棄用 Firestore Rules 測試、Firebase config 瀏覽器動態輸入框與多角色權限矩陣。

---

## [1.1.0] - 2026-07-14

- 導入 users Profile、角色權限與拒絕缺失/停用 Profile 的登入流程。
- 重寫 Firestore Rules、移除瀏覽器動態 Firebase 設定，新增測試、CI 與部署文件。

---

## [1.0.0] - 2026-07-07

- 前端 React/Vite + TypeScript 專案初始化與 PWA 設定。
- 建立五大資料型別 Zod 規格與 RWD 營運面板。
