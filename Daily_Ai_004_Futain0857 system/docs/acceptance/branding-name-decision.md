# 品牌與系統統一名稱決策紀錄 (Branding Name Decision)

# PENDING USER DECISION

- **建立日期**：2026-07-22
- **狀態**：`PENDING USER DECISION` (等待使用者明確指示統一品牌名稱，嚴禁自動批次修改)

---

## 🔍 現有專案出現之名稱盤點

目前專案程式、設定檔與交付文檔中，出現以下三種名稱衍生：

### 1. 「富田貨櫃出租」/「富田貨櫃出租系統」
- **畫面與組件位置**：
  - `container-rental-app-v1/src/pages/LoginPage.tsx` (登入頁標題)
  - `container-rental-app-v1/src/components/layout/Sidebar.tsx` (側欄 Brand 標題)
  - `container-rental-app-v1/src/components/layout/Topbar.tsx` (頂欄標題 `富田貨櫃`)
  - `container-rental-app-v1/src/components/layout/MobileNavDrawer.tsx` (抽屜選單標題)
  - `container-rental-app-v1/vite.config.ts` (`manifest.webmanifest` 應用程式名稱 `富田貨櫃出租管理系統`)
- **文件位置**：
  - `docs/user/quick-start.md`
  - `docs/user/user-operation-manual.md`
  - `docs/admin/deployment-manual.md`
  - `docs/admin/backup-restore.md`
  - `docs/admin/troubleshooting.md`
  - `docs/acceptance/customer-acceptance-test.md`
  - `docs/acceptance/known-limitations.md`
  - `docs/release/release-notes-v1.0.0-rc1.md`
  - `docs/DEPLOYMENT.md`
  - `docs/TEST_REPORT.md`

### 2. 「福田貨櫃倉儲」
- **文件位置**：
  - `docs/plans/000-index-modules-plans.md` (早期需求專案簡介與背景說明)

### 3. 「富田貨櫃倉儲」
- **檔案與資料夾位置**：
  - `PROJECT_SUMMARY.md` 與專案根目錄備註

---

## 🎯 待決策選項

1. **選項 A (推薦)**：統一使用 **「富田貨櫃出租系統」** (Futain Container Rental System)
2. **選項 B**：統一使用 **「福田貨櫃倉儲系統」** (Futain Storage System)
3. **選項 C**：統一使用 **「富田貨櫃倉儲出租系統」**

> ⚠️ 注意：未獲得使用者明確選擇前，本系統保持現狀，嚴禁對程式碼進行跨檔案批次取代更名。
