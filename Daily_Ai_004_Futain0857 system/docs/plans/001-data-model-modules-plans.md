---
plan_id: "001"
title: "資料模型與 API 定版"
status: "completed"
depends_on: []
format_version: 1
last_updated: "2026-07-21"
---

# 001 — 資料模型與 API 定版

## 目標

將目前六張工作表升級為可支援：

- 一份合約包含多個貨櫃
- 商品與費率方案
- 合約價格快照
- 租金與押金應收
- 一筆應收多次付款
- 續約、提前解約與退租結算
- 跨表稽核與防重複請求

## 不在本階段

- UI 全面改版
- 正式 GAS 部署
- 客戶入口
- 線上金流、電子簽章、LINE API
- 刪除 Legacy 工作表

## 新版 Google Sheets

```text
customers
containers
rate_plans
contracts
contract_items
invoices
payments
expenses
termination_records
audit_logs
request_logs
```

Legacy：

```text
rental_records
customer_ledgers
management_ledgers
```

Legacy 工作表在備份、Dry-run 與核對完成前不得刪除。

## Schema

### `rate_plans`

```text
rate_plan_id
name
container_size_ft
container_type
billing_cycle
contract_months
standard_monthly_price
contract_price
installment_count
default_deposit
first_year_discount
active
note
created_at
updated_at
deleted_at
```

### `contracts`

```text
contract_id
contract_no
customer_id
rate_plan_id
previous_contract_id
start_date
end_date
billing_cycle
rent_total
deposit_total
installment_count
status
actual_end_date
pricing_snapshot_json
terms_snapshot_json
note
created_at
updated_at
deleted_at
```

### `contract_items`

```text
contract_item_id
contract_id
container_id
unit_price
discount_amount
effective_price
start_date
end_date
status
created_at
updated_at
deleted_at
```

### `invoices`

```text
invoice_id
invoice_no
contract_id
customer_id
invoice_type
period_start
period_end
due_date
amount_due
amount_paid
balance_due
status
note
created_at
updated_at
voided_at
```

### `payments`

```text
payment_id
payment_no
invoice_id
contract_id
customer_id
payment_type
payment_method
payment_date
amount
bank_last_five
receipt_no
status
note
created_at
updated_at
voided_at
```

### `termination_records`

```text
termination_id
contract_id
requested_date
actual_end_date
inspection_status
remote_control_expected
remote_control_returned
damage_fee
cleaning_fee
other_fee
deposit_original
deposit_deducted
deposit_refunded
settlement_note
status
created_at
updated_at
```

### `request_logs`

```text
request_id
action
status
result_record_id
error_code
created_at
updated_at
expires_at
```

## 資料規則

1. 金額皆為整數新臺幣。
2. 日期使用 `YYYY-MM-DD`，時間使用 ISO timestamp。
3. 合約啟用時，費率與條款複製至快照欄位。
4. 有交易關聯的資料不得硬刪除。
5. `amount_paid` 與 `balance_due` 必須由付款紀錄重新計算。
6. 押金帳單與租金帳單使用不同 `invoice_type`。
7. 舊合約不得因費率方案修改而改變。
8. 一個 `container_id` 在重疊租期內只能存在一個有效合約項目。

## GAS 修改範圍

修改：

```text
apps-script/Setup.gs
apps-script/Router.gs
apps-script/Validation.gs
apps-script/SheetRepository.gs
apps-script/DashboardService.gs
apps-script/ManualTests.gs
```

新增：

```text
apps-script/RatePlansService.gs
apps-script/ContractsService.gs
apps-script/InvoicesService.gs
apps-script/PaymentsService.gs
apps-script/TerminationService.gs
apps-script/Migration.gs
```

## 前端修改範圍

新增型別：

```text
src/types/ratePlan.ts
src/types/contract.ts
src/types/contractItem.ts
src/types/invoice.ts
src/types/payment.ts
src/types/terminationRecord.ts
```

新增 API：

```text
src/services/api/ratePlansApi.ts
src/services/api/contractsApi.ts
src/services/api/invoicesApi.ts
src/services/api/paymentsApi.ts
src/services/api/terminationsApi.ts
```

API Response 必須使用 Zod 驗證，不可只做 TypeScript 斷言。

## 遷移腳本

```javascript
backupLegacySheets()
migrateLegacyRentalsToContracts({ dryRun: true })
migrateLegacyLedgersToInvoicesAndPayments({ dryRun: true })
verifyMigration()
```

### 遷移要求

- Dry-run 不得寫入。
- 正式遷移前建立時間戳備份工作表。
- 核對筆數、金額總計、孤兒外鍵與重複 ID。
- 遷移失敗不得刪除或覆蓋原始資料。
- 產生可讀的 Migration Report。

## 測試案例

- 同一合約建立兩筆 `contract_items`。
- 費率變更後舊合約快照不變。
- 一筆 24,000 元應收建立後餘額為 24,000。
- 無效 customer、container、rate plan 被拒絕。
- 重疊租期資料檢查可判斷衝突。
- `setupSpreadsheet()` 重複執行不破壞資料。
- 遷移 Dry-run 不寫入。

## 驗收條件

- [ ] 所有新版工作表可初始化。
- [ ] 多櫃合約資料關聯成立。
- [ ] 應收與付款分離。
- [ ] 費率與合約快照完成。
- [ ] Legacy 可 Dry-run 遷移。
- [ ] Migration Report 可核對。
- [ ] Lint、test、build 通過。
- [ ] API、Schema、Changelog 文件已更新。

## Antigravity IDE 執行指令

```text
先閱讀實際程式碼與本計畫，建立 Phase 001 差異分析。
只完成資料模型、型別、API 合約、初始化與遷移 Dry-run。
不得執行正式資料遷移，不得刪除 Legacy 工作表。
完成測試後停止並回報。
```
