# Production 部署門禁審查清單 (Production Gate Checklist)

# Production Status: BLOCKED

- **專案版本**：`v1.0.0-rc1`
- **當前門禁狀態**：`BLOCKED` (生產環境部署暫停，等待 TEST 環境人工實際驗證與使用者正式授權)
- **審查日期**：2026-07-22

---

## 🔒 生產環境發布門禁審核表 (Production Gate Items)

| 門禁類別 | 審核項目內容 | 門禁審查狀態 | 審查說明 |
| :---: | --- | :---: | --- |
| **環境隔離** | 獨立 TEST Google Spreadsheet 建立與 Schema 初始化 | `[ ]` | 待人工點擊建立試算表副本 |
| **環境隔離** | TEST GAS Web App 獨立部署與存取權限 (Anyone) | `[ ]` | 待人工於 GAS 介面執行發布 |
| **端到端實測** | 真實 Browser ➔ TEST GAS ➔ Sheets 完整 16 步驟 E2E 驗證 | `[ ]` | 待於真實連線環境操作演練 |
| **一致性與安全** | 全 API `requestId` 冪等防重複寫入真實驗證 | `[ ]` | 後端邏輯通過，待線上實測 |
| **併發與狀態** | 排他鎖 (`LockService`) 併發撞櫃阻擋與狀態機白名單 | `[ ]` | 測試案例 PASS，待線上實測 |
| **Session 控管** | Session Token 24小時過期阻擋與 UNAUTHORIZED 跳轉 | `[ ]` | 單元測試 PASS，待線上實測 |
| **Audit 保護** | `audit_logs` 唯讀保護與直接 CRUD 拒絕驗證 | `[ ]` | 單元測試 PASS，待線上實測 |
| **PWA 與離線** | PWA 可安裝性、Service Worker 快取與離線警告彈窗 | `[x]` | 前端打包與斷網邏輯已驗證 |
| **實機與 RWD** | Android Chrome / iPhone Safari 390px 實機操作驗證 | `[ ]` | 待於實體手機瀏覽器驗收 |
| **CSV 報表** | 6 類別 UTF-8 BOM CSV (客戶/貨櫃/合約/帳單/付款/支出) | `[x]` | 匯出工具與頁面按鈕配置完成 |
| **備份與還原** | 實做一次測試試算表備份與還原演練 | `[x]` | 已記錄於 `BACKUP_RESTORE.md` |
| **資安與 Secret** | 敏感資訊全檢 (Secrets, Passwords, Token 未寫入 Git) | `[x]` | `git grep` 掃描零洩漏 |
| **Production 授權** | 使用者明確書面核准 Production 部署指令 | `[ ]` | **目前尚未獲得核准 (BLOCKED)** |
| **Production 煙霧** | Production 上線後 12 步驟 Smoke Test 煙霧測試 | `[ ]` | 待發布後執行 |
| **初始備份** | Production 初始空白與基礎資料備份 | `[ ]` | 待發布後執行 |

---

> ⚠️ **警告**：目前 Production Status 標示為 `BLOCKED`。未經使用者明確發出 Production 部署指令前，嚴禁執行任何正式環境之部署動作。
