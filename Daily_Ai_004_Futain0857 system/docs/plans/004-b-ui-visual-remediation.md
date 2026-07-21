# 004-B — UI 視覺修正與對比度重做計畫 (Visual Remediation Plan)

- **建立日期**：2026-07-21
- **對應階段**：Phase 004-B (補強修復計畫)
- **原則**：不得自動進入 Phase 005，嚴格針對 UI/UX 視覺對比、Topbar/Sidebar 深藍架構、SVG 圖示替換與色彩層級進行重構修正。

---

## 1. 視覺問題源頭與錯誤 Class 盤點

透過比對全專案組件，盤點出以下樣式衝突與色彩涵蓋問題：

### 1.1 Topbar 背景與文字對比
- **問題**：`Topbar.tsx` 使用了白色背景 (`bg-white`) 與深灰文字 (`text-text-primary`)，未符合企業深藍品牌規範。
- **修正目標**：`Topbar` 改為深藍品牌背景 (`bg-brand-navy-950` / `#071B4A`)、白/金高對比文字與半透明深藍搜尋輸入框。

### 1.2 Sidebar 文字與 Logo 對比度過低
- **問題**：`Sidebar.tsx` 部分次要文字使用了 `text-slate-400` / `text-slate-300`，在深藍背景下 WCAG 對比度未達標。
- **修正目標**：標題與主選單採用純白 (`#ffffff`) 與經典金色 (`#c0b19b`)，選單懸停改為高亮 `hover:bg-brand-navy-800 hover:text-white`。

### 1.3 全系統 Emoji 簡陋圖示問題
- **問題**：大量組件使用原生 Emoji (`📊`, `👥`, `📦`, `📜`, `💰`, `🔑`, `🏷️`, `🛠️`, `⚙️`, `🏗️`, `🚪`, `🔍`)，顯得不合企業級專業後台風範。
- **修正目標**：建立 `src/components/ui/Icons.tsx` 模組，統一提供精美的向量 SVG 經典圖示集，取代全系統 Emoji。

### 1.4 Dashboard 視覺層級與卡片深淺衝突
- **問題**：`DashboardPage.tsx` 部分區塊色調雜亂，缺乏明確視覺焦點與層級。
- **修正目標**：淺灰背景 (`#f3f6fa`) + 純白立體卡片 (`#ffffff`) + 深藍頂部裝飾條，建立鮮明的資訊架構。

---

## 2. 預計修改與重構之檔案清單

1. **`src/components/ui/Icons.tsx`** (新建，提供全系統 15+ 個專業 SVG 向量圖示)
2. **`src/components/layout/Topbar.tsx`** (重構為深藍高對比 Topbar)
3. **`src/components/layout/Sidebar.tsx`** (重構為深藍底、高對比白/金高亮選單)
4. **`src/components/layout/MobileNavDrawer.tsx`** (重構深藍抽屜與 SVG 圖示)
5. **`src/components/layout/navConfig.ts`** (圖示類型改為 SVG Icon identifier)
6. **`src/components/layout/AppShell.tsx`** (整合深藍 Topbar 與深藍 Sidebar)
7. **`src/components/ui/` 下 10 大組件** (替換 Emoji 為專業 SVG，調整對比度)
8. **`src/components/dashboard/TodayTasks.tsx`** (替換圖示與警訊區塊)
9. **`src/components/contracts/ContractWizard.tsx` & `TerminationWizard.tsx`** (替換圖示與對比度修復)
10. **`src/pages/` 下 12 個頁面** (替換 Emoji 與舊版 slate Classes)

---

## 3. 修正執行順序與防護機制

1. 建立 `src/components/ui/Icons.tsx` 專業 SVG 圖示庫。
2. 重構 `Topbar`, `Sidebar`, `MobileNavDrawer`, `AppShell` 確定深藍 Header + 深藍 Sidebar + 淺灰 Content + 白卡片。
3. 逐頁替換 Emoji 為向量 SVG，並刪除舊有低對比度 `slate-300 / slate-400`。
4. 執行 `npm run lint`, `npm run test`, `npm run build` 自動化驗收。
