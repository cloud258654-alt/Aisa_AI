---
plan_id: "003"
title: "資料一致性、安全與稽核"
status: "completed"
depends_on: ["001", "002"]
format_version: 1
last_updated: "2026-07-21"
---

# 003 — 資料一致性、安全與稽核

## 目標

在 Google Sheets 架構下避免：

- 同一貨櫃重複出租
- 重複合約或收款
- 跨表只更新一半
- 任意狀態修改
- Session 偽造或過期後仍可操作
- 稽核紀錄被修改

## 1. Lock 與最新資料重查

所有寫入類 Service：

```javascript
var lock = LockService.getScriptLock();
lock.waitLock(10000);

try {
  // 鎖內重新讀取最新資料
  // 驗證
  // 完成全部跨表寫入
  SpreadsheetApp.flush();
} finally {
  lock.releaseLock();
}
```

不得只依賴前端先前讀取的狀態。

## 2. 冪等控制

每個寫入 Request 必須包含：

```text
requestId
```

適用：

- 建立／啟用合約
- 產生應收
- 登記／作廢付款
- 續約
- 退租
- 押金退款
- 貨櫃檢查結果

`request_logs` 行為：

| 狀態 | 行為 |
|---|---|
| 不存在 | 建立 PROCESSING 後執行 |
| PROCESSING | 拒絕同一請求重複執行 |
| SUCCESS | 回傳先前結果 |
| FAILED | 不自動重跑，要求新 requestId |

## 3. 狀態機

### Container

```text
AVAILABLE
RESERVED
RENTED
INSPECTION
MAINTENANCE
BLOCKED
RETIRED
```

### Contract

```text
DRAFT
ACTIVE
ENDING
ENDED
CANCELLED
```

### Invoice

```text
UNPAID
PARTIAL
PAID
VOID
```

### Payment

```text
CONFIRMED
VOID
REFUNDED
```

每個狀態轉換由後端白名單控制。

## 4. Session

完成：

- Token 簽章驗證
- 到期時間
- 登出失效
- 密碼變更後舊 Token 失效
- 登入失敗節流
- Session 過期時前端導回登入
- 不回傳 Salt、Hash 或 Secret
- Script Properties 不提交 Git

若 MVP 仍為單一管理員，文件必須明示尚未支援多角色 RBAC。

## 5. Audit Log

欄位：

```text
audit_id
operator
action
table_name
record_id
before_json
after_json
request_id
created_at
```

要求：

- Audit 不開放一般 CRUD。
- 登入成功、登入失敗、合約、付款、續約、退租與設定變更必須記錄。
- 敏感內容需遮蔽。
- JSON 過長時保留必要欄位及摘要。

## 6. 錯誤與復原

統一錯誤碼：

```text
BAD_REQUEST
UNAUTHORIZED
SESSION_EXPIRED
NOT_FOUND
CONFLICT
DUPLICATE_REQUEST
INVALID_STATE
VALIDATION_ERROR
INTERNAL_SERVER_ERROR
```

跨表操作失敗時：

1. 記錄失敗步驟。
2. 不回傳成功。
3. 寫入可追蹤 requestId。
4. 提供管理員復原或重試方式。
5. 不將 Sheet 名稱、行號、Secret 暴露給前端。

## 測試案例

- 同時建立同一貨櫃租約。
- 同一 requestId 連點兩次。
- 同一付款 Request 重送。
- 非法 `RENTED → AVAILABLE`。
- 已結束合約重新啟用。
- Session 過期及偽造。
- Audit API 修改嘗試。
- 模擬中間步驟錯誤。

## 驗收條件

- [ ] 重複租約只有一份成功。
- [ ] 重複付款只有一筆。
- [ ] 跨表失敗可被偵測與追蹤。
- [ ] 非法狀態轉換被拒絕。
- [ ] Session 過期無法存取。
- [ ] Audit 不可被一般 API 修改。
- [ ] 錯誤訊息不洩漏內部資訊。
- [ ] 安全與一致性測試寫入 `TEST_REPORT.md`。

## Antigravity IDE 執行指令

```text
對所有寫入 Service 進行一致性與安全盤點。
先補測試，再實作 Lock、Flush、requestId、狀態機與 Session 強化。
不得在未測試的情況下批次改寫全部 Service。
完成後停止並列出仍無法做到真正資料庫交易的已知限制。
```
