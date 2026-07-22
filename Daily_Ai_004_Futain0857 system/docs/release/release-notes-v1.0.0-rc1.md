# 福田貨櫃倉儲出租系統 — Release Candidate Notes v1.0.0-rc1

- **Version**: `v1.0.0-rc1`
- **Status**: `Release Candidate`
- **Production**: `Not Yet Approved` (BLOCKED)
- **Phase 005**: `verification-pending`
- **Date**: 2026-07-22

> ⚠️ 注意：本版次為 **v1.0.0-rc1 預備發行候選版本 (Release Candidate)**。專案開發與文件編寫已全數完成，但正式 PRODUCTION 部署尚未獲得使用者核准，請勿將本版本視為正式上線交付檔。

---

## 📋 功能性變更與收尾清單

### 1. 核心營運與 API 模型
- 支援多櫃合約快照、多管道對帳（轉帳/現金/LINE Pay）、續約鏈結與 7 步驟退租結算。
- 完成大寫 Canonical 狀態正規化 (`AVAILABLE`, `RENTED`, `INSPECTION`, `MAINTENANCE`, `UNPAID`, `PARTIAL`, `PAID`, `VOID`)。

### 2. 資料一致性與資安防護
- 後端 `StateMachine.gs` 白名單預檢與 `LockService` 併發撞櫃阻擋。
- 全寫入 API `requestId` 冪等防重複點擊控制。
- `audit_logs` 唯讀防護與 HMAC Signed Token 24 小時會期控管。

### 3. 深藍/金色 SaaS UI/UX 與 PWA
- 全面採用企業級深藍背景 (`#071B4A` / `#021341`)、經典金色 (`#9b9074` / `#c0b19b`) 與純白立體卡片。
- 建置 `Icons.tsx` 圖示庫，15+ 向量 SVG 圖示全數替換全站 Emoji。
- Vite PWA Plugin 預快取與離線寫入阻擋警示。
- 快捷登入防護：僅於本機開發/測試環境 (`DEV / TEST`) 顯示，正式 Production 打包模式自動隱藏。

### 4. 報表與文件齊備
- 完成 6 大類別 UTF-8 BOM CSV 報表匯出 (Excel 中文無亂碼)。
- 完成 30 項 UAT 驗收測試案例矩陣 (現標記為 `PENDING` 待實測驗收)。
- 完成 `handover-checklist.md`, `production-gate-checklist.md`, `branding-name-decision.md` 與完整 User/Admin 手冊。
