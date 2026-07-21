# Phase 003 — 資料一致性、安全與稽核 (已完成工作與交接紀錄)

- **完成日期**：2026-07-21
- **執行階段**：Phase 003 (`003-consistency-security-modules-plans.md`)
- **驗收狀態**：`VERIFIED & PASSED` (已由使用者完成實際驗收與確認)

---

## 📋 1. 八大必測安全與一致性案例驗證結果

| 案例 | 案例描述 | 測試結果 | 關鍵驗收細節 |
| :---: | --- | :---: | --- |
| **案例 1** | 併發撞櫃衝突 (同時建立兩份使用相同貨櫃的合約) | ✅ `PASS` | `LockService` 鎖內重讀狀態，第一份成功鎖櫃，第二份嘗試建立時觸發 `CONFLICT` (貨櫃非空閒狀態) 被成功阻擋。 |
| **案例 2** | `requestId` 冪等合約 (同一 `requestId` 連續送出兩次建立合約) | ✅ `PASS` | `request_logs` 紀錄狀態由 `PROCESSING` 轉為 `SUCCESS`；第二筆請求直接回傳先前合約結果，合約總筆數保持 1 筆無重複產生。 |
| **案例 3** | `requestId` 冪等付款 (同一 `requestId` 重複送出付款) | ✅ `PASS` | 第二筆重複請求直接回傳先前付款紀錄，付款紀錄筆數不增加。 |
| **案例 4** | 非法狀態轉變阻擋 (嘗試將 `RENTED` 貨櫃直接更新為 `AVAILABLE`) | ✅ `PASS` | 後端 `StateMachine.gs` 檢查觸發 `INVALID_STATE` (`非法狀態轉變 (container): 禁止由 RENTED 直接變更為 AVAILABLE`) 並阻擋寫入。 |
| **案例 5** | 非法狀態轉變阻擋 (嘗試將 `ENDED` 合約重新改為 `ACTIVE`) | ✅ `PASS` | `StateMachine.gs` 檢查觸發 `INVALID_STATE` (`非法狀態轉變 (contract): 禁止由 ENDED 直接變更為 ACTIVE`) 並阻擋寫入。 |
| **案例 6** | Session 到期鑑權阻擋 (過期或無效 Token 呼叫受保護 API) | ✅ `PASS` | `Router.gs` 驗證 Token 失敗回傳 `UNAUTHORIZED` 拒絕存取，前端 `gasClient` 捕捉後清理存取憑證並引導登入。 |
| **案例 7** | Audit Logs 修改保護 (嘗試透過一般 CRUD 修改 `audit_logs`) | ✅ `PASS` | `Router.gs` 針對 `table === 'audit_logs'` 之 `create/update/softDelete` 拋出 `UNAUTHORIZED` (`禁止透過一般 CRUD API 修改或刪除審計日誌`)。 |
| **案例 8** | 狀態正規化 Dry-run 測試 | ✅ `PASS` | `normalizeStatusToUppercase({ dryRun: true })` 成功掃描並回傳需正規化之欄位報告，且不改寫或破壞 Google Sheets 資料庫內容。 |

---

## 📁 2. 異動與新增檔案清單

### 2.1 Google Apps Script 後端 (`apps-script/`)
- `StateMachine.gs` (新增)：實作 Canonical 大寫狀態集與 `validateStatusTransition()` 狀態機轉換白名單。
- `Idempotency.gs` (新增)：實作 `checkAndLockRequestId()`, `updateRequestIdSuccess()`, `updateRequestIdFailed()` 提供 `PROCESSING/SUCCESS/FAILED` 狀態控制。
- `ContractsService.gs` (修改)：導入 `LockService` 鎖內重讀狀態、`SpreadsheetApp.flush()` 與 `requestId` 冪等處理。
- `PaymentsService.gs` (修改)：導入 `LockService`、`CONFIRMED/VOID` 大寫狀態與 `requestId` 冪等處理。
- `InvoicesService.gs` (修改)：狀態統一為 `UNPAID/PARTIAL/PAID/VOID` 大寫計算與對帳。
- `TerminationService.gs` (修改)：退租、結算、貨櫃檢查解鎖導入全流程 `LockService` 與 `requestId` 冪等處理。
- `SheetRepository.gs` (修改)：`updateRecord()` 整合狀態機轉變預檢與大寫正規化。
- `Router.gs` (修改)：寫入 `audit_logs` 一般 CRUD 權限阻擋 (`UNAUTHORIZED`)。
- `Migration.gs` (修改)：新增 `normalizeStatusToUppercase(options)` 支援 `dryRun`。
- `ManualTests.gs` (修改)：新增 `testPhase003ConsistencyAndSecurity()` 八大必測案例。

### 2.2 前端應用程式 (`container-rental-app-v1/src/`)
- `src/types/container.ts`, `contract.ts`, `contractItem.ts`, `invoice.ts`, `payment.ts`：型別更新為大寫 Canonical Status Union Types。
- `src/services/api/contractsApi.ts`, `invoicesApi.ts`, `paymentsApi.ts`：Zod Schema 更新支援大寫狀態解構解析。
- `tests/workflows.test.ts`：更新為大寫狀態斷言測試。

### 2.3 工程與專案管理文件 (`container-rental-app-v1/project_management/`)
- `CHANGELOG.md`：新增 `[1.5.0] - 2026-07-21` Phase 003 異動記錄。
- `TEST_REPORT.md`：新增 2.6 節 Phase 003 八大必測案例結果。
- `AUTH_PLAN.md`：新增單一管理員與未支援 RBAC 限制說明。

---

## 🧪 3. 測試與驗收結果

1. **ESLint 程式碼風格檢查**：`npm run lint` ➔ **PASS** (0 errors)
2. **Vitest 單元與流程測試**：`npm run test` ➔ **PASS** (3 test files, 15 tests passed)
3. **TypeScript & Vite 靜態與 PWA 建置**：`npm run build` ➔ **PASS** (靜態打包成功產出至 `dist/`)
4. **GAS 後端案例測試**：`testPhase003ConsistencyAndSecurity` ➔ **PASS** (8/8 八大必測案例全數通過)

---

## 🤝 4. 系統已知限制與後續計畫說明 (Known Limitations)

1. **Google Sheets 非真實 ACID 資料庫**：
   - 雖然已透過 `LockService.getScriptLock()` (10 秒逾時) 與 `SpreadsheetApp.flush()` 達到全域排他寫入與最新資料強制寫回，但在 GAS 超高併發或腳本強制中止時，無法提供如 PostgreSQL / MySQL 之真正原子交易 Rollback (回滾)。
2. **單一管理員模式 (Single Admin System)**：
   - 目前 Session 驗證為單一管理員登入憑證，**尚未支援多角色權限與 RBAC (Role-Based Access Control) 存取控制矩陣**（已於 `AUTH_PLAN.md` 明確標示）。
