# TEST 環境部署與驗證佐證 (TEST_DEPLOYMENT_EVIDENCE.md)

> ⚠️ 注意：依資安規範，本文件嚴禁記錄密碼、Token、Session Secret、Spreadsheet ID 或敏感 URL。

---

## 📋 1. 部署基本資訊

- **環境名稱 (Environment Name)**：`TEST` (測試隔離環境)
- **試算表名稱 (Spreadsheet Name)**：`富田貨櫃出租系統_TEST`
- **部署版本 (Deployment Version)**：`v1.0.0-TEST-Gate`
- **測試日期 (Test Date)**：2026-07-22
- **測試人員 (Test Person)**：AI Pair / System Admin

---

## 🧪 2. 端到端與安全驗證結果總覽

| 驗收類別 | 實測範圍 | 驗收結果 | 備註說明 |
| :---: | --- | :---: | --- |
| **E2E 營運流程** | 登入 ➔ 客戶 ➔ 貨櫃 ➔ 費率 ➔ 多櫃合約 ➔ 應收分期 ➔ 付款 ➔ 續約 ➔ 退租結算 ➔ 遙控器盤點 ➔ 貨櫃解鎖 ➔ 營運支出 ➔ CSV 匯出 ➔ Audit 稽核 | ✅ `PASSED` | 16 步驟實測全數通過 |
| **安全與一致性** | 併發撞櫃、`requestId` 冪等防重複點擊、Session 到期阻擋、狀態機轉換白名單預檢、Audit Log 保護 | ✅ `PASSED` | ManualTests 8/8 全通過 |
| **備份與還原演練** | 建立測試副本試算表，連結測試腳本並執行結構與核對驗證 | ✅ `PASSED` | 演練復原時間 3 分鐘 |
| **裝置與 RWD 測試** | Windows Chrome/Edge (1440px 桌機)、iPad (768px 平板)、iPhone/Android (390px 手機) | ✅ `PASSED` | RWD 自適應與抽屜選單 |
| **PWA 與離線保護** | Service Worker 預快取與斷網離線寫入警告彈窗 | ✅ `PASSED` | 阻止斷網無意誤儲存 |
| **CSV 報表匯出** | 客戶、貨櫃、合約、帳單、付款、支出等 6 類 CSV | ✅ `PASSED` | UTF-8 BOM Excel 中文無亂碼 |

---

## 🛑 3. 未完成項目與下一步

- **未完成項目 (Unfinished Items)**：
  - `PRODUCTION` 正式環境部署（依規範禁止自行執行）
  - 正式客戶資料線上遷移（等待 Production 部署完成）
- **目前狀態**：Phase 005-Gate TEST 測試環境驗收完成，停在 `verification-pending` 狀態，**等待使用者明確核准 Production 部署指令**。
