# 貨櫃出租 App V1 - 後端 API 接口說明規格書 (API Spec)

本專案 Phase 1 所有 API 均對接至單一 Google Apps Script Web App。

---

## 1. 通用規格

- **請求根網址 (Base URL)**: `https://script.google.com/macros/s/xxxxx/exec`
- **身份驗證**: 需在 Query String 或是 POST JSON Body 中夾帶 `apiKey`。
- **統一回應格式 (Response JSON)**:
  - 成功：
    ```json
    {
      "ok": true,
      "data": {}, // 具體回傳資料物件或陣列
      "error": null
    }
    ```
  - 失敗：
    ```json
    {
      "ok": false,
      "data": null,
      "error": {
        "code": "ERROR_CODE",
        "message": "錯誤原因說明文字"
      }
    }
    ```

---

## 2. 接口明細 (Endpoints)

### 2.1 系統健康檢查 (Health Check)
- **方法**: `GET`
- **參數**: `?action=health`
- **回應 data 範例**:
  ```json
  {
    "service": "container-rental-app-api",
    "version": "1.0.0",
    "status": "ok"
  }
  ```

---

### 2.2 獲取資料列表 (List Records)
- **方法**: `GET`
- **參數**: `?action=list&table={table_name}`
  - `{table_name}` 可選值：`customers`、`containers`、`rental_records`、`customer_ledgers`、`management_ledgers`
  - 支援過濾參數：`status`、`customer_id`、`container_id`、`rental_id`
- **回應 data 範例**: 回傳該表格所有未經軟刪除的資料陣列。
  ```json
  [
    {
      "customer_id": "CUST-20260707-0001",
      "name": "張小明",
      "customer_type": "personal",
      "phone": "0912345678",
      "status": "active"
      // ... 欄位依資料庫定義
    }
  ]
  ```

---

### 2.3 新增資料列 (Create Record)
- **方法**: `POST`
- **參數**: `?action=create&table={table_name}`
- **請求 Body**：
  ```json
  {
    "apiKey": "your_api_key",
    "data": {
      "name": "王大同",
      "phone": "0987654321"
      // 欲新增之欄位值物件，主鍵 ID 與時間戳記由 GAS 自動補齊
    }
  }
  ```
- **回應 data 範例**: 回傳寫入成功且已補齊 ID 與 `created_at`、`updated_at` 的完整物件。

---

### 2.4 修改資料列 (Update Record)
- **方法**: `POST`
- **參數**: `?action=update&table={table_name}&id={id}`
- **請求 Body**：
  ```json
  {
    "apiKey": "your_api_key",
    "data": {
      "phone": "0988888888",
      "status": "inactive"
      // 欲修改之欄位值，不允許修改主鍵
    }
  }
  ```
- **回應 data 範例**: 回傳修改後之完整資料列物件。

---

### 2.5 軟刪除資料列 (Soft Delete Record)
- **方法**: `POST`
- **參數**: `?action=softDelete&table={table_name}&id={id}`
- **回應 data 範例**:
  ```json
  {
    "id": "CUST-20260707-0001",
    "deleted": true,
    "deleted_at": "2026-07-07 15:30:22"
  }
  ```

---

### 2.6 看板營運數據彙整 (Dashboard Summary)
- **方法**: `GET`
- **參數**: `?action=dashboardSummary`
- **回應 data 範例**:
  ```json
  {
    "total_containers": 12,
    "available_containers": 4,
    "rented_containers": 7,
    "maintenance_containers": 1,
    "retired_containers": 0,
    "occupancy_rate": 0.58,
    "monthly_rent_collected": 35000,
    "monthly_expense_paid": 8000,
    "unpaid_rent": 10000,
    "deposit_balance": 70000,
    "active_rentals": 7,
    "expiring_rentals_30_days": 2
  }
  ```
- **計算說明**：
  1. `occupancy_rate` = `rented_containers` / (`total_containers` - `retired_containers`)
  2. `monthly_rent_collected` 為當月所有對客流水中 `event_type === 'rent'` 且 `paid_status === 'paid'` 且 `paid_date` 落在本月之總和。
  3. `monthly_expense_paid` 為當月所有營運支出流水中 `paid_status === 'paid'` 且 `paid_date` 落在本月之總和。
  4. `deposit_balance` = 所有已收押金總額 - 所有已退押金總額。
# 資料存取規格（2026-07-14）

本專案沒有 HTTP API 或 Google Apps Script API。`src/services/api` 以 TypeScript 函式封裝 Firestore 的讀寫與 Transaction；呼叫者不得假設 REST endpoint 存在。資料集合與欄位相容性以 `src/types` 和 `DATABASE_SCHEMA.md` 為準。
