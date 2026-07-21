# 貨櫃出租 App V1 - 資料庫欄位設計書 (Database Schema)

本文件定義系統資料欄位架構，升級至 Phase 001 支援多櫃合約、費率方案、應收與付款分離、結算與稽核日誌。

---

## 1. 主檔：客戶資料表 (`customers`)

| 欄位名稱 (Column) | 資料型態 (GAS) | 欄位說明 | 限制 / 預設值 |
|---|---|---|---|
| `customer_id` | String | 客戶唯一識別號 | PK, 格式: `CUST-YYYYMMDD-XXXX` |
| `name` | String | 客戶姓名或公司行號 | Not Null |
| `customer_type` | String | 客戶類型 | `personal` (個人), `business` (企業) |
| `phone` | String | 聯絡電話 | Not Null |
| `line_id` | String | LINE ID | Nullable |
| `email` | String | 電子郵件信箱 | Nullable |
| `tax_id` | String | 統一編號 | Nullable (企業用戶使用) |
| `billing_address` | String | 帳單郵寄地址 | Not Null |
| `status` | String | 客戶狀態 | `active` (使用中), `inactive` (已停用), `blacklisted` (黑名單) |
| `note` | String | 備註說明 | Nullable |
| `created_at` | DateTime | 建立時間 | YYYY-MM-DD HH:mm:ss |
| `updated_at` | DateTime | 更新時間 | YYYY-MM-DD HH:mm:ss |
| `deleted_at` | DateTime | 軟刪除時間 | Nullable (若無則留空) |

---

## 2. 主檔：貨櫃主檔表 (`containers`)

| 欄位名稱 (Column) | 資料型態 (GAS) | 欄位說明 | 限制 / 預設值 |
|---|---|---|---|
| `container_id` | String | 貨櫃唯一識別號 | PK, 格式: `CONT-YYYYMMDD-XXXX` |
| `container_no` | String | 貨櫃編號 (如 A01) | Not Null, Unique |
| `size_ft` | Number | 尺寸 (呎) | e.g. 10, 20, 40 |
| `container_type` | String | 貨櫃規格種類 | `standard` (標準櫃), `refrigerated` (冷凍櫃), `open_top` (開頂櫃) |
| `location_zone` | String | 存放園區區域 | e.g. A區, B區 |
| `location_label` | String | 具體位置標記 | e.g. A-12, B-03 |
| `total_setup_cost`| Number | 購置與改裝成本 | 預設: 0 |
| `status` | String | 貨櫃目前營運狀態 | `available` (空櫃), `rented` (出租中), `maintenance` (維修中), `retired` (停用) |
| `note` | String | 備註說明 | Nullable |
| `created_at` | DateTime | 建立時間 | YYYY-MM-DD HH:mm:ss |
| `updated_at` | DateTime | 更新時間 | YYYY-MM-DD HH:mm:ss |
| `deleted_at` | DateTime | 軟刪除時間 | Nullable (若無則留空) |

---

## 3. 交易表：租賃紀錄表 (`rental_records`)

| 欄位名稱 (Column) | 資料型態 (GAS) | 欄位說明 | 限制 / 預設值 |
|---|---|---|---|
| `rental_id` | String | 租約合約唯一識別號 | PK, 格式: `RENT-YYYYMMDD-XXXX` |
| `customer_id` | String | 承租客戶識別碼 | FK -> `customers.customer_id` |
| `container_id` | String | 承租貨櫃識別碼 | FK -> `containers.container_id` |
| `start_date` | String | 租期起算日 | YYYY-MM-DD |
| `end_date` | String | 預計租約截止日 | YYYY-MM-DD, Nullable |
| `billing_cycle` | String | 計費繳款週期 | `monthly` (按月), `quarterly` (按季), `yearly` (按年) |
| `monthly_rent` | Number | 每期/每月租金金額 | Not Null |
| `deposit_amount` | Number | 押金總額 | Not Null |
| `payment_due_day` | Number | 每月收款基準日 | 1-28, 預設: 5 (每月5號前需繳款) |
| `free_period_start`| String | 免收租金起日 | YYYY-MM-DD, Nullable |
| `free_period_end` | String | 免收租金迄日 | YYYY-MM-DD, Nullable |
| `status` | String | 合約目前狀態 | `draft` (草稿), `active` (租賃中), `ended` (已退租結案), `cancelled` (已取消) |
| `ended_date` | String | 實際辦理退租日 | YYYY-MM-DD, Nullable |
| `note` | String | 合約特別條款備註 | Nullable |
| `created_at` | DateTime | 建立時間 | YYYY-MM-DD HH:mm:ss |
| `updated_at` | DateTime | 更新時間 | YYYY-MM-DD HH:mm:ss |
| `deleted_at` | DateTime | 軟刪除時間 | Nullable (若無則留空) |

---

## 4. 交易表：對客帳務流水表 (`customer_ledgers`)

| 欄位名稱 (Column) | 資料型態 (GAS) | 欄位說明 | 限制 / 預設值 |
|---|---|---|---|
| `ledger_id` | String | 帳單明細唯一識別號 | PK, 格式: `CL-YYYYMMDD-XXXX` |
| `rental_id` | String | 關聯租約識別碼 | FK -> `rental_records.rental_id`, Nullable |
| `customer_id` | String | 客戶識別碼 | FK -> `customers.customer_id` |
| `container_id` | String | 貨櫃識別碼 | FK -> `containers.container_id` |
| `event_type` | String | 科目型態 | `rent` (租金), `deposit_in` (收押金), `deposit_out` (退押金), `late_fee` (違約金), `cleaning_fee` (清潔費), `discount` (折讓), `adjustment` (帳務調整) |
| `amount` | Number | 金額 | 應收/收退金額為正數 |
| `paid_status` | String | 付款入帳狀態 | `paid` (已收款), `unpaid` (未付欠款), `partial` (部分付款), `cancelled` (已取消) |
| `period_start` | String | 該期計費開始日 | YYYY-MM-DD (如租金所屬月份) |
| `period_end` | String | 該期計費結束日 | YYYY-MM-DD |
| `due_date` | String | 應收款繳款截止日 | YYYY-MM-DD |
| `paid_date` | String | 實際收款入帳日 | YYYY-MM-DD, Nullable |
| `payment_method` | String | 款項支付管道 | e.g. `cash`, `bank_transfer`, `line_pay` |
| `receipt_no` | String | 發票/收據單號 | 亦可存放 Google Drive 雲端電子收據連結 |
| `note` | String | 備註說明 | Nullable |
| `created_at` | DateTime | 建立時間 | YYYY-MM-DD HH:mm:ss |
| `updated_at` | DateTime | 更新時間 | YYYY-MM-DD HH:mm:ss |
| `deleted_at` | DateTime | 軟刪除時間 | Nullable (若無則留空) |

---

## 5. 交易表：管理支出流水表 (`management_ledgers`)

| 欄位名稱 (Column) | 資料型態 (GAS) | 欄位說明 | 限制 / 預設值 |
|---|---|---|---|
| `ledger_id` | String | 支出唯一識別號 | PK, 格式: `ML-YYYYMMDD-XXXX` |
| `container_id` | String | 關聯特定貨櫃 | FK -> `containers.container_id`, Nullable (全場公攤共用費則留空) |
| `expense_type` | String | 費用支出類型 | `maintenance` (貨櫃修繕), `land_rent` (場地地租), `utilities` (水電照明), `security` (保全監控), `ads` (廣告行銷), `cleaning` (清潔整理), `transport` (搬運), `renovation` (裝潢改裝), `other` (其他) |
| `vendor` | String | 收款廠商/商家名稱 | Not Null |
| `amount` | Number | 支出金額 | 正數 |
| `paid_status` | String | 付款結清狀態 | `paid` (已付清), `unpaid` (未付), `cancelled` (已取消) |
| `record_date` | String | 費用登記發生日期 | YYYY-MM-DD |
| `due_date` | String | 應支付截止日 | YYYY-MM-DD |
| `paid_date` | String | 實際付款日期 | YYYY-MM-DD, Nullable |
| `payment_method` | String | 付款管道 | e.g. `cash`, `bank_transfer` |
| `receipt_no` | String | 發票收據憑證編號 | 可放置 Google Drive 發票照片連結 |
| `is_capitalized` | Boolean | 是否資本化項目 | TRUE (增值資本化/列入資產), FALSE (一般費用列支) |
| `issue_desc` | String | 支出說明 (如維修詳情) | Not Null |
| `created_at` | DateTime | 建立時間 | YYYY-MM-DD HH:mm:ss |
| `updated_at` | DateTime | 更新時間 | YYYY-MM-DD HH:mm:ss |
| `deleted_at` | DateTime | 軟刪除時間 | Nullable (若無則留空) |

---

## 6. 前端 IndexedDB 本地同步資料表 (`offline_queue`)

為支援手機現場離線操作，IndexedDB 除快取上述五張表外，另建立離線佇列以維持網路回復後的資料同步：

| 欄位名稱 (Field) | 資料型態 | 欄位說明 | 備註 |
|---|---|---|---|
| `offline_id` | Number | 離線流水號 | 主鍵, 自動遞增 (Auto Increment) |
| `target_table` | String | 目標工作表名稱 | `customers`, `containers`, `rental_records`, `customer_ledgers`, `management_ledgers` |
| `action_type` | String | 資料操作行為 | `create` (新增), `update` (更新), `softDelete` (軟刪除) |
| `id` | String | 目標資料 ID | 例如 `CUST-20260707-0001` (用於更新或刪除路由定位) |
| `payload` | Object | 資料主體 JSON | 包含要發送至後端的欄位物件 |
| `created_at` | String | 離線登記日期 | ISO 字串 |
| `sync_status` | String | 同步狀態 | `pending` (待同步), `syncing` (同步中), `synced` (已完成), `failed` (同步失敗) |
| `retry_count` | Number | 嘗試上傳次數 | 預設: 0 |
| `last_error` | String | 上一次上傳錯誤訊息 | 可於設定頁面直接排查錯誤原因 |
