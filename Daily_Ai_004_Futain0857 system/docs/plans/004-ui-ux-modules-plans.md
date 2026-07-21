---
plan_id: "004"
title: "UI／UX 與操作者流程"
status: "completed"
depends_on: ["001", "002", "003"]
format_version: 1
last_updated: "2026-07-21"
---

# 004 — UI／UX 與操作者流程

## 目標

將已確認的 UI 示意圖落實為：

- 深藍、金色、白色企業風格
- 桌機、平板、手機 RWD
- 一眼看到今日待辦與財務風險
- 以流程導向完成建約、收款、續約及退租
- 共用元件與一致狀態顯示

## 品牌色票

```css
:root {
  --brand-navy-950: #021341;
  --brand-navy-900: #091945;
  --brand-navy-800: #101e45;
  --brand-slate-700: #333d57;

  --brand-gold-600: #81765f;
  --brand-gold-500: #9b9074;
  --brand-gold-300: #c0b19b;

  --surface-page: #f3f6fa;
  --surface-card: #ffffff;
  --surface-muted: #eef2f7;
  --border-default: #d9e1ec;

  --text-primary: #172033;
  --text-secondary: #667085;
  --text-on-dark: #ffffff;

  --status-success: #15803d;
  --status-warning: #b7791f;
  --status-danger: #b42318;
  --status-info: #2563eb;
}
```

將色票寫入 Tailwind theme，禁止各頁散落不同 Hex。

## 桌機架構

```text
Topbar：頁名｜搜尋｜通知｜使用者
Sidebar：深藍背景，金色 Active
Main：淺灰底＋白色卡片
```

選單：

1. 營運儀表板
2. 客戶管理
3. 貨櫃管理
4. 租約管理
5. 客戶帳務
6. 營運支出
7. 報表分析
8. 文件中心
9. 系統設定

## 手機架構

- Sidebar 改 Drawer。
- 表格轉 Card List。
- 表單單欄。
- 觸控目標至少 44px。
- Wizard 顯示清楚的當前步驟。
- 重要操作可用固定 Bottom Action Bar。

## Dashboard

### 今日待辦

- 今日到期
- 已逾期
- 30 天內到期合約
- 待續約
- 待退租檢查
- 維修中貨櫃

每張待辦卡可跳到已套用篩選條件的清單。

### KPI

- 貨櫃總數
- 可出租
- 出租中
- 出租率
- 本月應收
- 本月實收
- 未收餘額
- 押金保管餘額
- 本月支出

### 快速操作

- 建立客戶
- 建立合約
- 登記收款
- 辦理退租
- 新增支出

## 頁面要求

### 客戶

- 搜尋姓名、電話、統編及 LINE ID。
- 顯示合約、應收、付款及押金摘要。
- 詳情頁使用 Tabs 顯示歷史。
- 停用客戶不得建立新合約。

### 貨櫃

- 依狀態、尺寸、類型及區域篩選。
- 顯示目前客戶、合約期間及價格。
- 出租中不得直接改為可出租。
- 狀態 Badge 不只靠顏色，需有文字。

### 合約

- 草稿、啟用、待退租、結束及取消。
- 一筆合約顯示所有貨櫃。
- 顯示租金、押金、未收及下一到期日。
- 詳情含完整時間軸。

### 帳務

- 分為「應收帳單」與「收款紀錄」。
- 逾期、部分付款及已結清清楚顯示。
- 可由未收帳單直接登記付款。
- 押金不混入租金收入。

### 合約與退租 Wizard

建立合約：

```text
客戶 → 貨櫃 → 費率租期 → 押金分期 → 預覽 → 完成
```

退租：

```text
退租資訊 → 未結帳款 → 檢查 → 遙控器 → 扣款退款 → 確認
```

## 共用元件

```text
src/components/
├── layout/AppShell.tsx
├── layout/Sidebar.tsx
├── layout/Topbar.tsx
├── layout/MobileNavDrawer.tsx
├── ui/PageHeader.tsx
├── ui/StatCard.tsx
├── ui/StatusBadge.tsx
├── ui/DataTable.tsx
├── ui/MobileRecordCard.tsx
├── ui/SearchFilterBar.tsx
├── ui/EmptyState.tsx
├── ui/LoadingState.tsx
├── ui/ErrorState.tsx
├── ui/ConfirmDialog.tsx
├── dashboard/TodayTasks.tsx
├── contracts/ContractWizard.tsx
└── contracts/TerminationWizard.tsx
```

## UI 狀態

每頁必須有：

- Loading
- Empty
- Error
- Validation Error
- Success feedback
- Session expired
- Duplicate submission
- Offline
- Mobile layout

危險操作二次確認：

- 作廢合約
- 作廢帳單
- 作廢付款
- 退款
- 結束租約
- 貨櫃停用或維修

## 可用性

- WCAG AA 對比。
- 不只以顏色表示狀態。
- 錯誤訊息靠近欄位。
- 金額千分位、日期格式一致。
- 提交時鎖定按鈕防重複。
- 主要功能可用鍵盤操作。
- 手機不顯示壓縮到不可讀的表格。

## 驗收條件

- [ ] UI Token 集中管理。
- [ ] Dashboard 符合已確認示意圖風格。
- [ ] 1440px、768px、390px 可操作。
- [ ] 合約與退租 Wizard 可完成流程。
- [ ] 所有頁面具備 Loading、Empty、Error。
- [ ] 手機表格採 Card List 或有效響應式。
- [ ] 危險操作有確認。
- [ ] Lint、test、build 通過。
- [ ] 將畫面截圖及規格存入 `project_management/`。

## Antigravity IDE 執行指令

```text
先建立 Design Tokens 與共用元件，再逐頁套用。
不得先以大量頁面複製貼上完成改色。
每完成一個主要頁面，同時補桌機、平板、手機驗收。
完成後輸出各頁截圖清單與不一致項目。
```
