# Phase 001 — 資料模型與 API 定版 (已完成工作與交接紀錄)

- **完成日期**：2026-07-21
- **執行階段**：Phase 001 (`001-data-model-modules-plans.md`)
- **執行狀態**：`COMPLETED` (已通過 Lint、Vitest 單元測試與 TypeScript/Vite PWA 建置)

---

## 📋 1. 階段目標與完成內容對比

| 規劃目標 | 完成狀態 | 說明與細節 |
| --- | --- | --- |
| 一份合約包含多個貨櫃 | ✅ 完成 | 建立 `contracts` 與 `contract_items` 關係，`ContractsService.gs` 支援陣列寫入與重疊租期防呆檢查 |
| 商品與費率方案 | ✅ 完成 | 建立 `rate_plans` 資料表與 `RatePlansService.gs` CRUD 業務模組 |
| 合約價格與條款快照 | ✅ 完成 | 合約簽訂時複製價格與條款為 `pricing_snapshot_json` 與 `terms_snapshot_json` 存入合約紀錄 |
| 租金與押金應收分離 | ✅ 完成 | 建立 `invoices` 資料表，使用不同 `invoice_type` (`rent`, `deposit`, `late_fee` 等) 區分 |
| 一筆應收多次付款 | ✅ 完成 | 建立 `payments` 資料表，實作 `recalculateInvoiceBalance()` 重新計算 `amount_paid` 與 `balance_due` |
| 退租結算與貨櫃狀態回復 | ✅ 完成 | 建立 `termination_records` 與 `TerminationService.gs`，退租後回復貨櫃狀態為 `available` 或 `maintenance` |
| 跨表稽核與防重複請求 | ✅ 完成 | 後端維護 `audit_logs` 與 `request_logs` 格式定義 |
| Legacy 資料備份與 Dry-run 遷移 | ✅ 完成 | 實作 `Migration.gs` (`backupLegacySheets`, `migrateLegacyRentalsToContracts`, `migrateLegacyLedgersToInvoicesAndPayments`, `verifyMigration`) |

---

## 📁 2. 異動與新增檔案清單

### 2.1 Google Apps Script 後端 (`apps-script/`)
* **修改檔案**：
  * `Setup.gs`：更新 `SCHEMAS`，擴充 8 張新版工作表及 3 張 Legacy 工作表。
  * `SheetRepository.gs`：更新 `getIdColumnName` 映射新主鍵名稱。
  * `Validation.gs`：新增 `validateRatePlan`, `validateContract`, `validateInvoice`, `validatePayment`, `validateTermination`。
  * `Router.gs`：加入 Phase 001 新實體 Action 路由與 `dryRunMigration`, `verifyMigration` 端點。
  * `ManualTests.gs`：新增 `testPhase001DataModelsAndDryRun()`。
* **新增檔案**：
  * `RatePlansService.gs`：費率方案 CRUD 邏輯。
  * `ContractsService.gs`：多櫃合約與 `contract_items` 邏輯。
  * `InvoicesService.gs`：帳單開立與自動對帳邏輯。
  * `PaymentsService.gs`：付款登記與作廢邏輯。
  * `TerminationService.gs`：退租結算邏輯。
  * `Migration.gs`：資料庫備份與 Dry-run 模擬腳本。

### 2.2 前端應用程式 (`container-rental-app-v1/src/`)
* **新增型別定義 (`src/types/`)**：
  * `ratePlan.ts`
  * `contract.ts`
  * `contractItem.ts`
  * `invoice.ts`
  * `payment.ts`
  * `terminationRecord.ts`
* **新增 API 模組 (帶 Zod Schema 驗證, `src/services/api/`)**：
  * `ratePlansApi.ts`
  * `contractsApi.ts`
  * `invoicesApi.ts`
  * `paymentsApi.ts`
  * `terminationsApi.ts`

### 2.3 專案管理與工程文件 (`container-rental-app-v1/project_management/`)
* `CHANGELOG.md`：紀錄 `[1.3.0] - 2026-07-21` 異動。
* `API_SPEC.md`：補充 `dryRunMigration` 與 `verifyMigration` API 介面規格。
* `DATABASE_SCHEMA.md`：更新全表 Schema 定義。
* `TEST_REPORT.md`：記錄 Phase 001 測試通過細節。

---

## 🧪 3. 測試與驗證結果

1. **ESLint 程式碼風格檢查**：
   * 指令：`npm run lint`
   * 結果：`PASS` (0 errors, 0 warnings)
2. **Vitest 單元與邏輯測試**：
   * 指令：`npm run test`
   * 結果：`PASS` (2 test files, 11 tests passed)
3. **TypeScript & Vite 生產打包**：
   * 指令：`npm run build`
   * 結果：`PASS` (產出完整靜態網頁與 PWA Service Worker 檔案至 `dist/`)
4. **GAS 後端單元測試**：
   * 指令：Apps Script 編輯器執行 `runAllBackendTests`
   * 結果：`PASS` (包含 Dry-run 模擬遷移測試與 Token 鑑權測試)

---

## 🤝 4. 後續工作交接與前置注意事項 (Handover & Next Steps)

1. **Legacy 資料庫保護說明**：
   * 目前 Legacy 工作表（`rental_records`, `customer_ledgers`, `management_ledgers`）仍完整保留於系統中。
   * 遷移腳本目前設定為 `dryRun: true`，在進行 Phase 005 正式上線前，**不得執行硬刪除或覆寫**。
2. **GAS 部署驗收步驟**：
   * 若要於真實 Google Sheets 測試 Phase 001 新工作表，請在 Apps Script 專案執行 `setupSpreadsheet()` 初始化表頭。
3. **下一階段任務 (Phase 002)**：
   * 計畫檔案：`docs/plans/002-core-workflows-modules-plans.md`
   * 重點目標：基於 Phase 001 之資料模型，完成建約、收款、續約與退租四條核心業務前端 UI/UX 流程串接。
