# 貨櫃出租公司 App V1：兩階段開發任務書

> **用途**：此文件提供給 Antigravity / AI IDE / 工程師執行。  
> **目標**：先用 Google Sheets + Google Drive 快速做出可展示與小規模試用的 MVP，再保留升級到正式資料庫 PostgreSQL 的路徑。  
> **核心原則**：App V1 先做「營運管理系統」，不做完整會計系統。  
> **資料表架構**：採用 `2 張主檔 + 3 張交易表`。

---

# 0. 專案總目標

請建立一套「貨櫃出租管理 App V1」，支援手機端與 PC 端使用。

系統需支援：

1. 客戶管理
2. 貨櫃管理
3. 租賃紀錄管理
4. 對客帳務流水：租金、押金、退押金、欠款
5. 管理支出流水：維修、地租、水電、保全、廣告
6. Dashboard：出租率、未收租金、本月收入、本月支出、押金餘額
7. RWD 響應式版型：手機、平板、PC 都能操作
8. PWA：可加入手機主畫面
9. 離線資料暫存：手機現場操作時，可暫存待同步資料
10. 第一階段先使用 Google Sheets + Google Drive
11. 第二階段保留升級 PostgreSQL 的資料結構與 API 抽象層

---

# 1. 兩階段開發策略

## 1.1 Phase 1：Google Sheets + Google Drive 快速 MVP

### 目標

先做出可操作 Demo / 小規模內部試用版。

### 技術架構

```text
Frontend：React + Vite + TypeScript
UI：RWD 響應式設計
PWA：vite-plugin-pwa
Local DB：IndexedDB / Dexie.js
API Layer：前端統一呼叫 src/services/api
Backend：Google Apps Script Web App
Database：Google Sheets
File Storage：Google Drive
Deploy：Vercel / GitHub Pages / Netlify
```

### Phase 1 適用情境

| 情境 | 是否適合 |
|---|---|
| 內部 Demo | 適合 |
| 1～3 人小規模試用 | 適合 |
| 老闆看 Dashboard | 適合 |
| 現場手機登記收款與維修 | 適合 |
| 多人高頻同時操作 | 不建議 |
| 正式大量營運 | 不建議長期使用 |

---

## 1.2 Phase 2：正式資料庫版本

### 目標

當 Phase 1 驗證流程後，升級為正式營運架構。

### 技術架構

```text
Frontend：沿用 React + Vite + TypeScript + PWA
API Layer：沿用 src/services/api，不大改前端頁面
Backend：Django / FastAPI / Node.js
Database：PostgreSQL
File Storage：Google Drive 或 S3 類型儲存
Deploy：Google Cloud Run / Render / Railway / VPS
```

### Phase 2 升級重點

1. 將 Google Sheets 改成 PostgreSQL。
2. Google Drive 只保留合約、照片、收據、報表等附件。
3. 加入正式登入權限。
4. 加入資料驗證、交易一致性、操作紀錄。
5. 加入正式 API 後端。
6. 可增加排程：每月自動產生租金應收。
7. 可增加報表匯出與月結快照。

---

# 2. 資料表架構：2+3 正式 App V1 架構

系統核心資料表固定為：

```text
customers
containers
rental_records
customer_ledgers
management_ledgers
```

## 2.1 資料表類型

| 類型 | 表格 | 用途 |
|---|---|---|
| 主檔 | `customers` | 客戶資料 |
| 主檔 | `containers` | 貨櫃資料 |
| 交易表 | `rental_records` | 租賃紀錄 |
| 交易表 | `customer_ledgers` | 對客帳務流水 |
| 交易表 | `management_ledgers` | 管理支出流水 |

---

# 3. Google Sheets 設計

Phase 1 請建立一份 Google Sheets，名稱建議：

```text
ContainerRentalApp_V1_Database
```

其中建立 5 個工作表：

```text
customers
containers
rental_records
customer_ledgers
management_ledgers
```

另可增加 2 個系統用工作表：

```text
settings
sync_logs
```

---

## 3.1 `customers` 工作表欄位

```csv
customer_id,name,customer_type,phone,line_id,email,tax_id,billing_address,status,note,created_at,updated_at,deleted_at
```

### 欄位說明

| 欄位 | 說明 |
|---|---|
| `customer_id` | 客戶唯一編號 |
| `name` | 客戶姓名或公司名稱 |
| `customer_type` | `personal`、`business` |
| `phone` | 電話 |
| `line_id` | LINE ID |
| `email` | Email |
| `tax_id` | 統一編號 |
| `billing_address` | 帳單地址 |
| `status` | `active`、`inactive`、`blacklisted` |
| `note` | 備註 |
| `created_at` | 建立時間 |
| `updated_at` | 更新時間 |
| `deleted_at` | 軟刪除時間，未刪除則空白 |

---

## 3.2 `containers` 工作表欄位

```csv
container_id,container_no,size_ft,container_type,location_zone,location_label,total_setup_cost,status,note,created_at,updated_at,deleted_at
```

### 狀態

| status | 中文 |
|---|---|
| `available` | 空櫃 |
| `rented` | 出租中 |
| `maintenance` | 維修中 |
| `retired` | 停用 |

---

## 3.3 `rental_records` 工作表欄位

```csv
rental_id,customer_id,container_id,start_date,end_date,billing_cycle,monthly_rent,deposit_amount,payment_due_day,free_period_start,free_period_end,status,ended_date,note,created_at,updated_at,deleted_at
```

### 狀態

| status | 中文 |
|---|---|
| `draft` | 草稿 |
| `active` | 租賃中 |
| `ended` | 已退租 |
| `cancelled` | 已取消 |

---

## 3.4 `customer_ledgers` 工作表欄位

```csv
ledger_id,rental_id,customer_id,container_id,event_type,amount,paid_status,period_start,period_end,due_date,paid_date,payment_method,receipt_no,note,created_at,updated_at,deleted_at
```

### event_type

| event_type | 中文 |
|---|---|
| `rent` | 租金 |
| `deposit_in` | 收押金 |
| `deposit_out` | 退押金 |
| `late_fee` | 違約金 |
| `cleaning_fee` | 清潔費 |
| `discount` | 折讓 |
| `adjustment` | 帳務調整 |

### paid_status

| paid_status | 中文 |
|---|---|
| `paid` | 已付 |
| `unpaid` | 未付 |
| `partial` | 部分付款 |
| `cancelled` | 已取消 |

---

## 3.5 `management_ledgers` 工作表欄位

```csv
ledger_id,container_id,expense_type,vendor,amount,paid_status,record_date,due_date,paid_date,payment_method,receipt_no,is_capitalized,issue_desc,created_at,updated_at,deleted_at
```

### expense_type

| expense_type | 中文 |
|---|---|
| `maintenance` | 貨櫃修繕 |
| `land_rent` | 場地地租 |
| `utilities` | 水電照明 |
| `security` | 保全監控 |
| `ads` | 廣告行銷 |
| `cleaning` | 清潔整理 |
| `transport` | 搬運運輸 |
| `renovation` | 裝潢改善 |
| `other` | 其他 |

---

# 4. Phase 1 後端：Google Apps Script Web API

請建立 Google Apps Script 專案，部署為 Web App。

## 4.1 Apps Script Web App 要求

### 部署設定

```text
Execute as：Me
Who has access：依測試需求設定
```

若是內部測試，可先使用受控權限。正式使用時需加入簡單 Token 驗證，避免公開 API 被濫用。

---

## 4.2 API 基本格式

所有 API 回應統一格式：

```json
{
  "ok": true,
  "data": {},
  "error": null
}
```

錯誤格式：

```json
{
  "ok": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "錯誤說明"
  }
}
```

---

## 4.3 必做 API

### Health Check

```text
GET /exec?action=health
```

回應：

```json
{
  "ok": true,
  "data": {
    "service": "container-rental-app-api",
    "version": "1.0.0"
  },
  "error": null
}
```

---

### 通用列表查詢

```text
GET /exec?action=list&table=customers
GET /exec?action=list&table=containers
GET /exec?action=list&table=rental_records
GET /exec?action=list&table=customer_ledgers
GET /exec?action=list&table=management_ledgers
```

要求：

1. 預設排除 `deleted_at` 不為空的資料。
2. 支援簡單 query string 篩選。
3. 至少支援 `status`、`customer_id`、`container_id`、`rental_id` 篩選。

---

### 通用新增

```text
POST /exec?action=create&table=customers
POST /exec?action=create&table=containers
POST /exec?action=create&table=rental_records
POST /exec?action=create&table=customer_ledgers
POST /exec?action=create&table=management_ledgers
```

要求：

1. 自動補 `created_at`。
2. 自動補 `updated_at`。
3. 如果前端沒給 ID，後端要產生 ID。
4. ID 格式建議：
   - `CUST-YYYYMMDD-XXXX`
   - `CONT-YYYYMMDD-XXXX`
   - `RENT-YYYYMMDD-XXXX`
   - `CL-YYYYMMDD-XXXX`
   - `ML-YYYYMMDD-XXXX`

---

### 通用更新

```text
POST /exec?action=update&table=customers&id=CUST-xxx
POST /exec?action=update&table=containers&id=CONT-xxx
POST /exec?action=update&table=rental_records&id=RENT-xxx
POST /exec?action=update&table=customer_ledgers&id=CL-xxx
POST /exec?action=update&table=management_ledgers&id=ML-xxx
```

要求：

1. 只更新傳入欄位。
2. 自動更新 `updated_at`。
3. 不允許直接修改 Primary Key。

---

### 軟刪除

```text
POST /exec?action=softDelete&table=customers&id=CUST-xxx
```

要求：

1. 不刪除列。
2. 只填入 `deleted_at`。
3. 前端列表預設不顯示已刪除資料。

---

## 4.4 Dashboard API

```text
GET /exec?action=dashboardSummary
```

應回傳：

```json
{
  "total_containers": 10,
  "available_containers": 3,
  "rented_containers": 6,
  "maintenance_containers": 1,
  "occupancy_rate": 0.6,
  "monthly_rent_collected": 30000,
  "monthly_expense_paid": 12000,
  "unpaid_rent": 5000,
  "deposit_balance": 60000,
  "active_rentals": 6,
  "expiring_rentals_30_days": 2
}
```

---

# 5. Phase 1 前端專案規格

## 5.1 建議專案名稱

```text
container-rental-app-v1
```

---

## 5.2 技術選型

請建立：

```text
React + Vite + TypeScript
```

建議套件：

```text
react-router-dom
vite-plugin-pwa
dexie
date-fns
zod
```

UI 可選：

```text
Tailwind CSS
或
純 CSS Modules
或
shadcn/ui
```

若使用 AI IDE 快速開發，建議使用 Tailwind CSS，以便快速做 RWD。

---

## 5.3 建議資料夾結構

```text
container-rental-app-v1/
├── public/
│   ├── icons/
│   └── manifest.webmanifest
├── src/
│   ├── app/
│   │   ├── App.tsx
│   │   └── router.tsx
│   ├── components/
│   │   ├── common/
│   │   ├── dashboard/
│   │   ├── customers/
│   │   ├── containers/
│   │   ├── rentals/
│   │   ├── customerLedgers/
│   │   └── managementLedgers/
│   ├── pages/
│   │   ├── DashboardPage.tsx
│   │   ├── CustomersPage.tsx
│   │   ├── ContainersPage.tsx
│   │   ├── RentalsPage.tsx
│   │   ├── CustomerLedgersPage.tsx
│   │   ├── ManagementLedgersPage.tsx
│   │   └── SettingsPage.tsx
│   ├── services/
│   │   ├── api/
│   │   │   ├── apiClient.ts
│   │   │   ├── customersApi.ts
│   │   │   ├── containersApi.ts
│   │   │   ├── rentalsApi.ts
│   │   │   ├── customerLedgersApi.ts
│   │   │   ├── managementLedgersApi.ts
│   │   │   └── dashboardApi.ts
│   │   └── storage/
│   │       ├── offlineDb.ts
│   │       └── offlineSync.ts
│   ├── types/
│   │   ├── customer.ts
│   │   ├── container.ts
│   │   ├── rentalRecord.ts
│   │   ├── customerLedger.ts
│   │   └── managementLedger.ts
│   ├── utils/
│   │   ├── date.ts
│   │   ├── money.ts
│   │   └── ids.ts
│   ├── styles/
│   │   └── globals.css
│   └── main.tsx
├── .env.example
├── package.json
├── vite.config.ts
└── README.md
```

---

# 6. 前端頁面需求

## 6.1 DashboardPage

### 必須顯示

1. 總貨櫃數
2. 可出租貨櫃數
3. 出租中貨櫃數
4. 維修中貨櫃數
5. 出租率
6. 本月已收租金
7. 本月已付支出
8. 未收租金
9. 押金餘額
10. 30 天內到期租賃

### RWD 要求

| 裝置 | 顯示方式 |
|---|---|
| PC | 4 欄卡片 |
| 平板 | 2 欄卡片 |
| 手機 | 1 欄卡片 |

---

## 6.2 CustomersPage

### 功能

1. 客戶列表
2. 新增客戶
3. 編輯客戶
4. 停用客戶
5. 搜尋客戶
6. 查看客戶帳務與租賃摘要

---

## 6.3 ContainersPage

### 功能

1. 貨櫃列表
2. 新增貨櫃
3. 編輯貨櫃
4. 修改貨櫃狀態
5. 依狀態篩選：空櫃、出租中、維修中、停用
6. 手機端以卡片顯示
7. PC 端以表格顯示

---

## 6.4 RentalsPage

### 功能

1. 建立租賃
2. 編輯租賃
3. 退租
4. 續租
5. 查看租賃到期日
6. 建立租賃時可選客戶與貨櫃
7. 建立租賃後自動將貨櫃狀態改成 `rented`

### 建立租賃流程

```text
選客戶
↓
選空櫃
↓
輸入起訖日期
↓
輸入月租金
↓
輸入押金
↓
輸入付款日
↓
建立 rental_records
↓
更新 containers.status = rented
↓
可選擇建立押金應收與第一期租金
```

---

## 6.5 CustomerLedgersPage

### 功能

1. 建立租金應收
2. 登記收款
3. 登記押金
4. 登記退押金
5. 查看未收租金
6. 依客戶、貨櫃、租賃、日期篩選
7. 標記已付款
8. 匯出 CSV

---

## 6.6 ManagementLedgersPage

### 功能

1. 登記支出
2. 登記維修
3. 登記地租
4. 登記水電保全
5. 登記廣告支出
6. 標記已付款
7. 依貨櫃、費用類型、日期篩選
8. 支援全場費用，`container_id` 可為空

---

## 6.7 SettingsPage

Phase 1 最少包含：

1. Google Apps Script API URL 設定說明
2. 同步狀態
3. 離線資料佇列
4. 版本資訊
5. 手動同步按鈕

---

# 7. RWD 與 PWA 規範

## 7.1 RWD

### 斷點建議

| 裝置 | 寬度 | UI |
|---|---|---|
| 手機 | `< 768px` | 單欄卡片、底部導覽 |
| 平板 | `768px ~ 1023px` | 雙欄 |
| PC | `>= 1024px` | Sidebar + 表格 |
| 大螢幕 | `>= 1440px` | 寬版 Dashboard |

---

## 7.2 PWA

必須支援：

1. `manifest.webmanifest`
2. App icon
3. Service Worker
4. 加入主畫面
5. 基礎離線開啟
6. 快取前端資源
7. 顯示目前網路狀態

---

## 7.3 離線資料暫存

### 原則

PWA 不保證所有平台都支援背景同步，尤其 iOS / Safari 不應完全依賴 Background Sync。

必須採用：

```text
IndexedDB 本地暫存
+
前景同步
+
手動重試
```

---

## 7.4 離線可操作項目

| 操作 | 是否允許 |
|---|---|
| 查看已快取客戶 | 允許 |
| 查看已快取貨櫃 | 允許 |
| 登記維修 | 允許，先進 offline_queue |
| 登記支出 | 允許，先進 offline_queue |
| 登記收款 | 允許，先進 offline_queue |
| 建立正式租賃 | 不建議離線 |
| 退租 | 不建議離線 |
| 刪除資料 | 不允許離線 |

---

## 7.5 offline_queue 結構

IndexedDB 中建立：

```text
offline_queue
```

欄位：

```text
offline_id
target_table
action_type
payload
created_at
sync_status
retry_count
last_error
```

狀態：

```text
pending
syncing
synced
failed
```

---

# 8. API 抽象層要求

前端不可在頁面元件中直接呼叫 Google Apps Script URL。  
所有 API 必須集中在：

```text
src/services/api/
```

原因：Phase 2 要從 Google Sheets 換成正式後端時，只需要替換 API 層，不要大改 UI。

## 8.1 apiClient.ts

請建立統一 API Client：

```ts
export async function apiGet<T>(params: Record<string, string>): Promise<T> {}

export async function apiPost<T>(
  params: Record<string, string>,
  body: unknown
): Promise<T> {}
```

`.env.example`：

```env
VITE_GAS_API_URL=https://script.google.com/macros/s/xxxxx/exec
VITE_APP_ENV=development
```

---

# 9. Google Drive 附件儲存規劃

Phase 1 可以先建立資料夾，但附件上傳可視時間決定是否實作。

Google Drive 資料夾：

```text
貨櫃出租App資料/
├── contracts/
├── receipts/
├── maintenance_photos/
├── reports/
└── backups/
```

## 9.1 Phase 1 最小做法

1. 先不做 App 內上傳。
2. 人工把合約、收據、維修照片放 Google Drive。
3. 在 `note` 或 `receipt_no` 欄位填入 Google Drive 檔案連結。

## 9.2 Phase 2 再做正式附件表

未來可新增：

```text
attachments
```

欄位：

```text
attachment_id
related_table
related_id
file_name
file_type
drive_file_id
drive_url
uploaded_by
created_at
deleted_at
```

---

# 10. Phase 2 資料庫升級規劃

## 10.1 PostgreSQL Table 名稱

Phase 2 沿用同樣表名：

```text
customers
containers
rental_records
customer_ledgers
management_ledgers
```

## 10.2 為什麼 Phase 1 也要用英文欄位

因為 Google Sheets 欄位要能直接映射到 PostgreSQL。

例如：

```text
customer_id → customers.customer_id
container_id → containers.container_id
rental_id → rental_records.rental_id
```

---

## 10.3 Phase 2 可新增資料表

| 表 | 用途 |
|---|---|
| `users` | 使用者登入 |
| `roles` | 權限角色 |
| `attachments` | 附件 |
| `audit_logs` | 操作紀錄 |
| `monthly_snapshots` | 月結快照 |
| `contract_change_logs` | 租金與合約異動紀錄 |

---

# 11. 驗收標準

## 11.1 Phase 1 MVP 驗收

必須做到：

| 項目 | 驗收條件 |
|---|---|
| 專案可啟動 | `npm install`、`npm run dev` 成功 |
| Dashboard | 可顯示 10 個核心指標 |
| 客戶管理 | 可新增、列表、編輯、停用 |
| 貨櫃管理 | 可新增、列表、編輯、修改狀態 |
| 租賃管理 | 可建立租賃，並更新貨櫃狀態 |
| 對客帳務 | 可新增租金、押金、收款紀錄 |
| 管理支出 | 可新增維修、地租、水電、廣告支出 |
| RWD | 手機、平板、PC 版型可正常使用 |
| PWA | 可加入主畫面，可離線開啟基本畫面 |
| 離線暫存 | 可建立 offline_queue 並顯示待同步資料 |
| API 抽象 | 所有 API 呼叫集中在 `src/services/api` |
| README | 有完整啟動與設定說明 |

---

## 11.2 Phase 2 驗收

Phase 2 不必現在開發，但 Phase 1 架構必須讓 Phase 2 能順利銜接。

驗收條件：

1. 前端不直接依賴 Google Sheets 結構。
2. API 層可以替換。
3. 資料欄位名稱可映射 PostgreSQL。
4. ID 與 enum 命名一致。
5. RWD / PWA 前端可沿用。
6. 離線佇列可改送正式後端 API。

---

# 12. 開發順序

請按照以下順序開發，不要跳階段。

## Step 1：建立前端專案

```bash
npm create vite@latest container-rental-app-v1 -- --template react-ts
cd container-rental-app-v1
npm install
npm run dev
```

---

## Step 2：安裝必要套件

```bash
npm install react-router-dom dexie date-fns zod
npm install -D vite-plugin-pwa
```

若使用 Tailwind CSS，請另外安裝與設定 Tailwind。

---

## Step 3：建立 types

建立：

```text
src/types/customer.ts
src/types/container.ts
src/types/rentalRecord.ts
src/types/customerLedger.ts
src/types/managementLedger.ts
```

---

## Step 4：建立 API Layer

建立：

```text
src/services/api/apiClient.ts
src/services/api/customersApi.ts
src/services/api/containersApi.ts
src/services/api/rentalsApi.ts
src/services/api/customerLedgersApi.ts
src/services/api/managementLedgersApi.ts
src/services/api/dashboardApi.ts
```

---

## Step 5：建立 Google Apps Script API

建立 `Code.gs`，完成：

1. `doGet`
2. `doPost`
3. `health`
4. `list`
5. `create`
6. `update`
7. `softDelete`
8. `dashboardSummary`

---

## Step 6：建立頁面

建立：

```text
DashboardPage
CustomersPage
ContainersPage
RentalsPage
CustomerLedgersPage
ManagementLedgersPage
SettingsPage
```

---

## Step 7：建立 RWD Layout

建立：

1. Desktop Sidebar
2. Mobile Bottom Navigation
3. Responsive Cards
4. Responsive Tables / Cards

---

## Step 8：建立 PWA

設定：

1. `vite-plugin-pwa`
2. `manifest.webmanifest`
3. icons
4. Service Worker
5. offline fallback

---

## Step 9：建立 IndexedDB Offline Queue

使用 Dexie 建立：

```text
offline_queue
cached_customers
cached_containers
cached_rental_records
```

---

## Step 10：測試與修正

測試：

1. PC Chrome
2. Android Chrome
3. iPhone Safari
4. macOS Safari / Chrome
5. 離線模式
6. 網路恢復同步
7. Google Sheets 資料是否正確寫入

---

# 13. 程式品質要求

1. 使用 TypeScript。
2. 所有資料型別放在 `src/types`。
3. 所有 API 放在 `src/services/api`。
4. 不要把 Google Apps Script URL 寫死在元件裡。
5. 表單需基本驗證。
6. 金額欄位需格式化。
7. 日期欄位需統一使用 `YYYY-MM-DD`。
8. enum 值使用英文，不使用中文存資料庫。
9. 中文只出現在 UI 顯示層。
10. 所有主要程式碼加入簡潔中文註解。
11. README 必須寫清楚如何啟動、如何設定 `.env`、如何部署 GAS。
12. 每完成一個階段，請在 `project_management/CHANGELOG.md` 寫紀錄。

---

# 14. 必須產出的文件

請建立：

```text
README.md
project_management/CHANGELOG.md
project_management/ARCHITECTURE.md
project_management/API_SPEC.md
project_management/DATABASE_SCHEMA.md
project_management/PHASE_2_MIGRATION_PLAN.md
```

## 14.1 README.md 必須包含

1. 專案目的
2. 技術架構
3. 安裝指令
4. 啟動指令
5. `.env` 設定方式
6. Google Apps Script 部署方式
7. Google Sheets 建立方式
8. PWA 測試方式
9. 已知限制

---

# 15. 已知限制

Phase 1 需在 README 明確寫出：

1. Google Sheets 不適合作為長期正式資料庫。
2. 多人高頻同時操作可能有同步與效能限制。
3. iOS PWA 不保證背景自動同步。
4. 附件上傳 Phase 1 可先採人工 Google Drive 連結。
5. 正式營運建議 Phase 2 升級 PostgreSQL。
6. 本系統 V1 是營運管理帳，不是完整會計系統。
7. 正式報稅仍需交由會計師或正式會計系統處理。

---

# 16. 最終交付要求

完成後請回報：

1. 專案資料夾結構
2. 已完成頁面
3. 已完成 API
4. Google Apps Script 部署 URL 設定方式
5. Google Sheets 工作表建立狀態
6. PWA 是否可安裝
7. RWD 測試結果
8. 離線佇列測試結果
9. 已知問題
10. 下一步建議

---

# 17. 一句話總結

```text
先用 React + PWA + Google Apps Script + Google Sheets / Drive 快速完成可操作 MVP，所有欄位與 API 命名必須保留未來升級 PostgreSQL 的一致性，避免 Phase 2 需要重寫整套系統。
```
