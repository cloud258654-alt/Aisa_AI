# 004 — UI/UX 現況盤點與差距分析報告 (Current Gap Analysis)

- **建立日期**：2026-07-21
- **對應計畫**：Phase 004 (`004-ui-ux-modules-plans.md`)
- **目的**：在進行 Phase 004 UI/UX 全面優化前，盤點現有系統佈局、色彩、元件、響應式與狀態體驗，並規劃不破壞既有核心業務邏輯的重構策略。

---

## 1. 現有路由與頁面清單 (Routes & Pages)

目前 `src/App.tsx` 定義之 11 個 Hash 路由與對應 12 個頁面組件：

| 路由路徑 | 頁面組件 | 主要功能職責 | 現況說明 |
| --- | --- | --- | --- |
| `/` | `DashboardPage.tsx` | 營運儀表板、KPI 與待辦事項 | 目前為舊版暗色卡片，缺乏整合型今日待辦與導向篩選 |
| `/customers` | `CustomersPage.tsx` | 客戶管理 (列表/新增/編輯/詳情) | 內含客戶搜尋、狀態與歷史分頁 |
| `/containers` | `ContainersPage.tsx` | 貨櫃管理 (列表/新增/維修/停用) | 內含尺寸與類型篩選 |
| `/rentals` | `RentalsPage.tsx` | 舊版租約管理 (Legacy 視圖) | 展示舊版單櫃租約視圖 |
| `/contracts` | `ContractsPage.tsx` | 核心合約啟用與續約管理 | Phase 002 新建之最小介面，待重構成 6 步驟 Wizard |
| `/invoices` | `InvoicesPage.tsx` | 應收帳單與付款對帳登記 | Phase 002 新建之最小介面，包含部分付款與作廢 |
| `/termination` | `TerminationPage.tsx` | 退租結算與貨櫃檢查解鎖 | Phase 002 新建之最小介面，待重構成 7 步驟 Wizard |
| `/rate-plans` | `RatePlansPage.tsx` | 費率方案與定價管理 | 獨立費率維護介面 |
| `/customer-ledgers` | `CustomerLedgersPage.tsx` | 客戶對帳單 (Legacy 視圖) | 展示傳統客戶帳單紀錄 |
| `/management-ledgers` | `ManagementLedgersPage.tsx` | 場地支出與營運費用管理 | 支出登記與維修費用統計 |
| `/settings` | `SettingsPage.tsx` | 系統設定與管理員資訊 | 包含 GAS 連線與 Session 資訊 |
| `/login` | `LoginPage.tsx` | 管理員登入驗證頁面 | 獨立居中卡片 |

---

## 2. 現有 Layout 與共用元件盤點

- **現有 Layout**：`src/components/common/Layout.tsx`
  - 桌機側邊欄 (Sidebar)：全黑背景 `bg-slate-950`，紫藍漸層選單。
  - 手機選單：底部導覽列 (Bottom Nav Bar)，僅呈現前 6 個功能。
  - 缺乏：獨立 `Topbar` (無全域搜尋、通知提示與頂部麵包屑)、獨立 `MobileNavDrawer` (手機側滑選單)。
- **現有共用元件**：目前僅有 `Layout.tsx` 一個共用組件，極度缺乏模組化與複用性。

---

## 3. 色彩與樣式差距 (Color Scheme Gap)

| 項目 | 目前現況 | 企業級 SaaS 品牌標準 (Phase 004 Target) |
| --- | --- | --- |
| **頁面整體背景** | 黑色/深藍色 `bg-slate-950` | 淺灰白色 `#f3f6fa` (`--surface-page`) |
| **卡片與內容容器** | 暗色玻璃 `bg-slate-900` / `glass-panel` | 純白卡片 `#ffffff` (`--surface-card`)，輔以淺灰外框 `#d9e1ec` |
| **側邊欄 (Sidebar)** | 暗灰藍色 `glass-panel` | 企業深藍 `#021341` (`--brand-navy-950`) / `#091945` (`--brand-navy-900`) |
| **重點與 Active 高亮** | 靛藍/紫色漸層 (`from-indigo-600 to-purple-600`) | 經典企業金色 `#9b9074` (`--brand-gold-500`) / `#c0b19b` (`--brand-gold-300`) |
| **主要文字顏色** | 亮白色 `text-slate-100` | 深灰藍色 `#172033` (`--text-primary`)；次級 `#667085` (`--text-secondary`) |
| **狀態顏色** | 任意 Tailwind 色碼 (red-500, green-400 等) | 規範化狀態色：成功 `#15803d`、警告 `#b7791f`、危險 `#b42318`、資訊 `#2563eb` |

---

## 4. UI 狀態與防護缺乏狀況 (Loading / Empty / Error / UX)

1. **Loading 狀態**：各頁各自使用簡單 `<div>載入中...</div>` 或 spinner，樣式不統一。
2. **Empty 狀態**：資料表空值時大多直接顯示空表格或簡陋文字，缺乏導向創建立之空白示意組件 (`EmptyState`)。
3. **Error 狀態**：錯誤跳出全域 `alert()` 或紅字區塊，缺乏友好的錯誤復原與重試組件 (`ErrorState`)。
4. **危險操作確認**：目前刪除或作廢多使用 `confirm()` 瀏覽器原生快顯，體驗粗糙，需替換為 `ConfirmDialog` 互動對話框。
5. **重複寫入防護**：表單送出時，部分按鈕缺乏高亮/停用/Loading 文字提示。

---

## 5. 響應式與跨裝置問題 (RWD Gap)

- **1440px 桌機**：表格寬度過寬時無邊界控制，資訊密度不均。
- **768px 平板**：選單與內容區塊容易互相擠壓。
- **390px 手機**：
  - 目前大部分頁面（`CustomersPage`, `ContainersPage`, `RentalsPage` 等）強制在手機渲染寬表格，造成橫向滾動或欄位文字壓縮不可讀。
  - 需要針對手機版將 `DataTable` 自動轉換或切換為 `MobileRecordCard` (單欄卡片式清單)。
  - 合約與退租流程在手機上缺乏分步引導 (Wizard) 與底部固定按鈕 (Bottom Action Bar)。

---

## 6. 元件重構與新增規劃

### 6.1 可保留與適度修改
- 後端通訊層：`gasClient.ts`, `contractsApi.ts`, `invoicesApi.ts`, `paymentsApi.ts`, `terminationsApi.ts` 完全保留。
- 狀態與 Context：`SessionContext.tsx`, `useSession.ts` 完全保留。

### 6.2 應重構之佈局組件
- `src/components/common/Layout.tsx` 拆解重構為：
  - `src/components/layout/AppShell.tsx`
  - `src/components/layout/Sidebar.tsx`
  - `src/components/layout/Topbar.tsx`
  - `src/components/layout/MobileNavDrawer.tsx`

### 6.3 應新增之標準共用 UI 元件 (`src/components/ui/`)
- `PageHeader.tsx` (標題與動作區)
- `StatCard.tsx` (KPI 統計卡片)
- `StatusBadge.tsx` (規範化狀態標籤，兼具文字與顏色)
- `DataTable.tsx` (桌機標準表格)
- `MobileRecordCard.tsx` (手機卡片式清單)
- `SearchFilterBar.tsx` (搜尋與多重篩選列)
- `EmptyState.tsx` (無資料無障礙提示)
- `LoadingState.tsx` (載入骨架/動態提示)
- `ErrorState.tsx` (錯誤復原提示)
- `ConfirmDialog.tsx` (危險操作二次確認對話框)

### 6.4 應新增之流程組件 (`src/components/dashboard/`, `src/components/contracts/`)
- `TodayTasks.tsx` (今日待辦與到期警訊)
- `ContractWizard.tsx` (6 步驟合約建立 Wizard：客戶 ➔ 貨櫃 ➔ 費率租期 ➔ 押金分期 ➔ 預覽 ➔ 完成)
- `TerminationWizard.tsx` (7 步驟退租結算 Wizard：退租資訊 ➔ 未結帳款 ➔ 檢查 ➔ 遙控器 ➔ 扣款退款 ➔ 確認)

---

## 7. 預計修改之檔案清單

1. `container-rental-app-v1/tailwind.config.js` (寫入全域 Design Tokens)
2. `container-rental-app-v1/src/index.css` (寫入企業級 CSS 變數與 Light Theme 基礎樣式)
3. `container-rental-app-v1/src/App.tsx` (替換使用 `AppShell`)
4. 新增 `src/components/layout/` 4 個檔案
5. 新增 `src/components/ui/` 10 個標準組件
6. 新增 `src/components/dashboard/TodayTasks.tsx`
7. 新增 `src/components/contracts/ContractWizard.tsx`, `TerminationWizard.tsx`
8. 更新 `src/pages/` 下 11 個營運頁面組件套用 Design System

---

## 8. 風險控管與避免破壞既有功能之策略

1. ** View 層完全隔離**：所有修改嚴格限定於 View/CSS/Component 呈現層，**絕不調整後端 Service 邏輯或變更 API 回傳結構**。
2. **`requestId` 介面持續保留**：在 Wizard 或表單送出時，繼續透傳 `requestId` 確保 Phase 003 寫入冪等。
3. **Zod Validation 嚴格保留**：前端所有表單送出前依然經過 Zod Schema 解析與型別驗證。
4. **狀態轉換約束保留**：不論 UI 如何設計，後端狀態機驗證與全域 `LockService` 依然是最終防線。
5. **漸進式驗收**：每完成一個核心模組，即進行 `npm run lint`、`npm run test` 與 `npm run build` 自動化測試，確保完全相容。
