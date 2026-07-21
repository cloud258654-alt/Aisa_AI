# 貨櫃出租 App V1 - 後端 API 接口說明規格書 (API Spec)

本專案使用 Google Apps Script Web App 作為後端。所有請求皆為 **POST** 發送至單一入口網址，並在 JSON body 中附帶 `action` 及 `sessionToken` 進行驗證。

---

## 1. 通用規格

- **請求方法**: `POST`
- **Content-Type**: `text/plain;charset=utf-8`
- **後端 API 網址 (VITE_GAS_WEB_APP_URL)**: `https://script.google.com/macros/s/xxxxx/exec`
- **請求 JSON 格式 (Body)**:
  ```json
  {
    "action": "actionName",
    "sessionToken": "your_session_token_here",
    "payload": {
      // 具體業務參數
    }
  }
  ```
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
        "message": "繁體中文錯誤說明"
      }
    }
    ```

---

## 2. API Actions 清單

### 2.1 系統健康檢查 (health)
* **無需登入**
* **Payload**: `{}`
* **回應 data 範例**:
  ```json
  {
    "status": "healthy",
    "timestamp": "2026-07-15 19:50:00"
  }
  ```

### 2.2 管理者登入 (login)
* **無需登入**
* **Payload**:
  ```json
  {
    "username": "admin",
    "password": "adminpassword"
  }
  ```
* **回應 data 範例**:
  ```json
  {
    "sessionToken": "payloadBase64.signatureBase64",
    "expiresAt": "2026-07-16T19:50:00.000Z"
  }
  ```
* **錯誤代碼**:
  - `INVALID_CREDENTIALS` (帳號或密碼錯誤)
  - `LOCKED_OUT` (登入失敗次數過多被鎖定)

### 2.3 管理者登出 (logout)
* **需登入**
* **Payload**: `{}`
* **回應 data 範例**:
  ```json
  {
    "success": true
  }
  ```

### 2.4 獲取資料清單 (list)
* **需登入**
* **Payload**:
  ```json
  {
    "table": "customers" // options: customers, containers, rental_records, customer_ledgers, management_ledgers
  }
  ```
* **回應 data 範例**: 回傳該表格所有未經軟刪除的資料陣列。

### 2.5 獲取單筆資料 (get)
* **需登入**
* **Payload**:
  ```json
  {
    "table": "containers",
    "id": "CONT-20260707-0001"
  }
  ```

### 2.6 新增資料列 (create)
* **需登入（在後端 Script Lock 中執行）**
* **Payload**:
  ```json
  {
    "table": "customers",
    "data": {
      "name": "王大同",
      "phone": "0987654321"
      // 依各資料型別定義
    },
    "createFirstMonthBill": true // 僅用於 table 為 rental_records 時，指定是否自動產生首期帳單與押金
  }
  ```

### 2.7 修改資料列 (update)
* **需登入（在後端 Script Lock 中執行）**
* **Payload**:
  ```json
  {
    "table": "containers",
    "id": "CONT-20260707-0001",
    "updates": {
      "status": "maintenance"
    }
  }
  ```

### 2.8 軟刪除資料列 (softDelete)
* **需登入（在後端 Script Lock 中執行）**
* **Payload**:
  ```json
  {
    "table": "customers",
    "id": "CUST-20260707-0001"
  }
  ```

### 2.9 退租合約結案 (terminateRental)
* **需登入（在後端 Script Lock 中執行）**
* **Payload**:
  ```json
  {
    "id": "RENT-20260707-0001",
    "endedDate": "2026-07-15",
    "note": "貨櫃清空無損"
  }
  ```

### 2.10 看板營運數據彙整 (dashboardSummary)
* **需登入**
* **Payload**: `{}`
* **回應 data 範例**:
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

### 2.11 試算表遷移模擬 (dryRunMigration)
* **需登入**
* **Payload**: `{}`
* **回應 data 範例**:
  ```json
  {
    "rentalsMigration": { "dryRun": true, "contractsCreated": 10, "itemsCreated": 10, "errors": [] },
    "ledgersMigration": { "dryRun": true, "invoicesCreated": 15, "paymentsCreated": 12, "errors": [] }
  }
  ```

### 2.12 遷移結果驗證 (verifyMigration)
* **需登入**
* **Payload**: `{}`
* **回應 data 範例**:
  ```json
  {
    "legacyRentalsCount": 10,
    "contractsCount": 10,
    "legacyLedgersCount": 15,
    "invoicesCount": 15,
    "paymentsCount": 12,
    "report": ["=== 遷移驗證報告 ==="]
  }
  ```

