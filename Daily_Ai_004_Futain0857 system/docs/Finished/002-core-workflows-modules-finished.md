# Phase 002 — 核心營運流程 (已完成工作與交接紀錄)

- **完成日期**：2026-07-21
- **執行階段**：Phase 002 (`002-core-workflows-modules-plans.md`)
- **執行狀態**：`COMPLETED` (已通過 Lint、Vitest 單元測試、GAS 案例測試與 TypeScript/Vite PWA 建置)

---

## 📋 1. 四大真實案例驗證結果

| 案例 | 案例描述 | 測試結果 | 關鍵驗收細節 |
| :---: | --- | :---: | --- |
| **案例 A** | 單櫃合約 (20 呎裸櫃、年租 48,000 元、押金 5,000 元、分兩期付款) | ✅ `PASS` | `ContractsService.gs` 單一交易成功生成 `active` 合約、1 個 `contract_item`、1 筆押金帳單 ($5,000) 與 2 期租金帳單 ($24,000/期)，貨櫃轉為 `rented` 狀態。 |
| **案例 B** | 多櫃同一合約 (同時承租 2 個 10 呎櫃) | ✅ `PASS` | 同一份合約成功包含 2 個 `contract_items` 紀錄 (`CNTI-B1`, `CNTI-B2`)，保留獨立貨櫃項目與價格，雙櫃均成功轉為 `rented`。 |
| **案例 C** | 部分付款至結清 (應收 24,000 元，首筆付 10,000 元，次筆付 14,000 元) | ✅ `PASS` | 登記首筆 $10,000 付款後帳單自動計算 `amount_paid` = $10,000, `balance_due` = $14,000, 狀態轉為 `PARTIAL` (`partial`)；登記次筆 $14,000 付款後 `balance_due` = $0, 狀態轉為 `PAID` (`paid`)。 |
| **案例 D** | 退租扣款與檢查狀態解鎖 (押金 10,000 元，遙控器 350 元，清潔費 1,000 元) | ✅ `PASS` | `startTermination` 時合約轉為 `ending`，貨櫃先轉入 `INSPECTION` (`inspection`) 狀態；`completeTermination` 試算扣款 $1,350 元，應退 $8,650 元；貨櫃未直接轉為 `available`，直至 `completeContainerInspection` 通過後始解鎖為 `AVAILABLE` (`available`)。 |

---

## 📁 2. 異動與新增檔案清單

### 2.1 Google Apps Script 後端 (`apps-script/`)
- `ContractsService.gs`：更新 `createAndActivateContract()` 與 `renewContract()`，實作單一業務 Service 合約啟用與續約。
- `PaymentsService.gs`：更新 `createPayment()` 與 `voidPayment()`，回傳最新帳單與動態對帳狀態。
- `InvoicesService.gs`：更新 `recalculateInvoiceBalance()` 回傳最新計算物件。
- `TerminationService.gs`：實作 `startTermination()`、`completeTermination()` 與 `completeContainerInspection()`。
- `Router.gs`：新增 `activateContract`, `recordPayment`, `voidPayment`, `renewContract`, `startTermination`, `completeTermination`, `completeContainerInspection` 路由轉發。
- `ManualTests.gs`：新增 `testPhase002WorkflowsCases()` 自動化案例測試。

### 2.2 前端應用程式 (`container-rental-app-v1/src/`)
- **新增頁面組件 (`src/pages/`)**：
  - `ContractsPage.tsx`：合約建立與續約介面。
  - `InvoicesPage.tsx`：帳單列表與付款登記 (部分付款/作廢) 介面。
  - `TerminationPage.tsx`：7 步驟退租 Wizard、遙控器與清潔費扣款計算、貨櫃檢查解鎖介面。
  - `RatePlansPage.tsx`：費率方案管理介面。
- **更新 API 通訊模組 (`src/services/api/`)**：
  - `contractsApi.ts`：匯出 `createAndActivateContract`, `renewContract`。
  - `paymentsApi.ts`：匯出 `createPayment`, `voidPayment`。
  - `terminationsApi.ts`：匯出 `startTermination`, `completeTermination`, `completeContainerInspection`。
- **新增 Vitest 流程測試 (`tests/`)**：
  - `tests/workflows.test.ts`：覆蓋 Cases A, B, C, D 之計算與 Zod 驗證。

### 2.3 工程與專案管理文件 (`container-rental-app-v1/project_management/`)
- `CHANGELOG.md`：紀錄 `[1.4.0] - 2026-07-21` 核心營運流程異動。
- `TEST_REPORT.md`：更新 2.5 節 Phase 002 四大案例測試結果。

---

## 🧪 3. 測試與驗收結果

1. **ESLint 程式碼風格檢查**：`npm run lint` ➔ **PASS** (0 errors)
2. **Vitest 單元與流程測試**：`npm run test` ➔ **PASS** (3 test files, 15 tests passed)
3. **TypeScript & Vite 靜態與 PWA 建置**：`npm run build` ➔ **PASS** (產出 static bundle 至 `dist/`)
4. **GAS 後端案例測試**：`testPhase002WorkflowsCases` ➔ **PASS** (Cases A, B, C, D 全數通過)

---

## 🤝 4. 工作交接與 Phase 003 前置說明

1. **Legacy 資料庫保護**：
   - 本階段完全沿用 Phase 001 Schema 與數據庫，`rental_records`, `customer_ledgers`, `management_ledgers` 舊表依然安全無損。
2. **Phase 003 重點目標 (`003-consistency-security-modules-plans.md`)**：
   - 強化 `requestId` 完整冪等寫入機制 (防止重複請求導致重複發單或扣款)。
   - 強化後端 Session 安全、操作權限、防並行撞櫃與 Auditing 稽核完整度。
