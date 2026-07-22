# 福田貨櫃倉儲出租系統 — 專案交付與交接 CheckList (Handover Checklist)

- **版本**：`v1.0.0-rc1`
- **最後更新日期**：2026-07-22

---

## 📋 專案交接檢核項目 (Handover Checklist)

| 分類 | 檢核項目 | 狀態 | 備註說明 |
| :---: | --- | :---: | --- |
| **代碼與版本** | GitHub Repository 提交與 Push | `[x]` | 工作目錄潔淨 (Working Tree Clean) |
| **代碼與版本** | 工作目錄無未追蹤暫存檔 (Working Tree Clean) | `[x]` | 通過 `git status` 檢查 |
| **權限與所有權** | Google Spreadsheet 試算表所有權移交 | `[ ]` | 待 Production 建立後移交所有權 |
| **權限與所有權** | Google Apps Script 專案所有權移交 | `[ ]` | 待 Production 部署後設定專案管理者 |
| **設定與資安** | Script Properties 集中管理與說明 | `[x]` | 已整理於 `deployment-manual.md` |
| **設定與資安** | 資安掃描：無任何 Secret/PASSWORD 出現在程式或文件 | `[x]` | 通過 `git grep` 敏感字串全檢 |
| **環境與網址** | 正式 Production 營運網址與網域設定 | `[ ]` | Production 尚未核准部署 |
| **環境與網址** | 正式管理員初始帳號與 Hash 設定指南 | `[x]` | 已記載於 `deployment-manual.md` |
| **備份與運維** | 備份位置與滾動備份 SOP | `[x]` | 已記載於 `BACKUP_RESTORE.md` |
| **操作與部署文件** | 使用者操作手冊與快速入門指南 (`docs/user/`) | `[x]` | `quick-start.md` & `user-operation-manual.md` |
| **操作與部署文件** | 管理員部署、備份與疑難排解手冊 (`docs/admin/`) | `[x]` | `deployment-manual.md` & `troubleshooting.md` |
| **驗收與簽核** | 客戶 30 項 UAT 真術驗收測試矩陣簽核 | `[ ]` | 矩陣已備妥，待客戶實際執行 UAT 簽核 |

---

> 註：未完成之所有權移交與 UAT 簽核項目，依規範保持未勾選 `[ ]` 狀態。
