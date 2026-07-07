# 貨櫃出租 App V1 - 第二階段資料庫遷移計劃 (Phase 2 Migration Plan)

本專案在 Phase 1 使用 Google Sheets 進行 MVP 驗證，當營運規模擴大、多人協作頻率提高時，建議啟動此遷移計劃升級至 **PostgreSQL + 正式後端 API**。

---

## 1. 遷移目標

1. 將後端資料儲存媒介由 Google Sheets 替換為 PostgreSQL。
2. 將 Google Apps Script API 替換為正式的高效能 API 後端（如 Python FastAPI, Django 或 Node.js Express）。
3. 導入完整的帳戶密碼登入 (Authentication) 與 RBAC 權限角色控管。
4. 沿用 Phase 1 前端 React + PWA 程式碼，僅調整 `.env` 連線配置。

---

## 2. PostgreSQL 資料表建置規格 (DDL)

由於 Phase 1 採用了與資料庫完全一致的欄位命名規範，直接使用以下 SQL 建置 Table 即可：

```sql
-- 1. Customers Table
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    customer_type VARCHAR(20) NOT NULL CHECK (customer_type IN ('personal', 'business')),
    phone VARCHAR(50) NOT NULL,
    line_id VARCHAR(100),
    email VARCHAR(150),
    tax_id VARCHAR(20),
    billing_address TEXT NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'inactive', 'blacklisted')),
    note TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 2. Containers Table
CREATE TABLE containers (
    container_id VARCHAR(50) PRIMARY KEY,
    container_no VARCHAR(50) UNIQUE NOT NULL,
    size_ft INTEGER NOT NULL,
    container_type VARCHAR(50) NOT NULL,
    location_zone VARCHAR(100) NOT NULL,
    location_label VARCHAR(100) NOT NULL,
    total_setup_cost NUMERIC(12, 2) DEFAULT 0,
    status VARCHAR(20) NOT NULL CHECK (status IN ('available', 'rented', 'maintenance', 'retired')),
    note TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 3. Rental Records Table
CREATE TABLE rental_records (
    rental_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL REFERENCES customers(customer_id),
    container_id VARCHAR(50) NOT NULL REFERENCES containers(container_id),
    start_date DATE NOT NULL,
    end_date DATE,
    billing_cycle VARCHAR(20) NOT NULL CHECK (billing_cycle IN ('monthly', 'quarterly', 'yearly')),
    monthly_rent NUMERIC(12, 2) NOT NULL,
    deposit_amount NUMERIC(12, 2) NOT NULL,
    payment_due_day INTEGER DEFAULT 5,
    free_period_start DATE,
    free_period_end DATE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('draft', 'active', 'ended', 'cancelled')),
    ended_date DATE,
    note TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 4. Customer Ledgers Table
CREATE TABLE customer_ledgers (
    ledger_id VARCHAR(50) PRIMARY KEY,
    rental_id VARCHAR(50) REFERENCES rental_records(rental_id),
    customer_id VARCHAR(50) NOT NULL REFERENCES customers(customer_id),
    container_id VARCHAR(50) NOT NULL REFERENCES containers(container_id),
    event_type VARCHAR(30) NOT NULL CHECK (event_type IN ('rent', 'deposit_in', 'deposit_out', 'late_fee', 'cleaning_fee', 'discount', 'adjustment')),
    amount NUMERIC(12, 2) NOT NULL,
    paid_status VARCHAR(20) NOT NULL CHECK (paid_status IN ('paid', 'unpaid', 'partial', 'cancelled')),
    period_start DATE,
    period_end DATE,
    due_date DATE NOT NULL,
    paid_date DATE,
    payment_method VARCHAR(50),
    receipt_no VARCHAR(255),
    note TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 5. Management Ledgers Table
CREATE TABLE management_ledgers (
    ledger_id VARCHAR(50) PRIMARY KEY,
    container_id VARCHAR(50) REFERENCES containers(container_id),
    expense_type VARCHAR(30) NOT NULL CHECK (expense_type IN ('maintenance', 'land_rent', 'utilities', 'security', 'ads', 'cleaning', 'transport', 'renovation', 'other')),
    vendor VARCHAR(255) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    paid_status VARCHAR(20) NOT NULL CHECK (paid_status IN ('paid', 'unpaid', 'cancelled')),
    record_date DATE NOT NULL,
    due_date DATE NOT NULL,
    paid_date DATE,
    payment_method VARCHAR(50),
    receipt_no VARCHAR(255),
    is_capitalized BOOLEAN DEFAULT FALSE,
    issue_desc TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);
```

---

## 3. 資料移轉步驟

1. **備份備妥**：
   - 於 Google Sheets 下載五張工作表（`customers`、`containers`、`rental_records`、`customer_ledgers`、`management_ledgers`）為 CSV 格式。
2. **清洗與校對**：
   - 確認日期格式符合 `YYYY-MM-DD`。
   - 確認布林值及數值符合 SQL 要求。
3. **匯入 PostgreSQL**：
   - 使用 SQL 工具（如 pgAdmin、DBeaver）或是簡單的 Python pandas 腳本，按照主檔優先的原則（`customers` 與 `containers` ➔ `rental_records` ➔ 交易表）匯入資料庫中。

---

## 4. API 端點替換與部署

1. **建置正式後端**：
   - 採用 FastAPI (Python) 建置後端服務，連線至 PostgreSQL。
   - 實作與 `Code.gs` 完全一致的端點路由與 Query 參數，以確保前端代碼免大幅改動：
     - `GET /api/v1/list` ➔ `GET /exec?action=list`
     - `POST /api/v1/create` ➔ `POST /exec?action=create`
     - `POST /api/v1/update` ➔ `POST /exec?action=update`
     - `POST /api/v1/softDelete` ➔ `POST /exec?action=softDelete`
     - `GET /api/v1/dashboardSummary` ➔ `GET /exec?action=dashboardSummary`
2. **跨來源資源共用 (CORS)**：
   - 於 FastAPI 程式碼中啟用 CORS Middleware，允許可信任的前端 URL 存取。
3. **前端設定更換**：
   - 修改前端的 `.env` 檔案：
     ```env
     VITE_GAS_API_URL=https://your-api-server.com/api/v1
     VITE_GAS_API_KEY=your_new_jwt_token_or_secret
     ```
   - 由於前端所有資料存取皆透過 `apiClient.ts` 抽象隔離，換上新 API URL 後系統即可完全恢復運作。
