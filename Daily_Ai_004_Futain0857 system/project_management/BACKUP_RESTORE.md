# 福田貨櫃倉儲出租系統 — 備份、還原與一致性核對指南 (BACKUP_RESTORE.md)

- **建立日期**：2026-07-22
- **適用環境**：TEST 與 PRODUCTION
- **維護負責人**：系統管理員

---

## 1. 備份策略 (Backup Strategy)

### 1.1 試算表每日自動備份
1. **備份頻率**：每日凌晨 03:00 (Asia/Taipei)
2. **備份方式**：
   - 透過 Google Drive 的「建立副本 (Make a copy)」功能，將正式環境之 Google Spreadsheet 複製一份備份至 `[Backup_Archive]` 資料夾。
   - 檔名命名規範：`Futain_Production_Spreadsheet_YYYYMMDD.xlsx`。
3. **保留天數**：至少保留 30 天滾動副本，每月 1 號保留一份永久年度備份。

### 1.2 指令碼與設定備份
1. **GAS 原始碼**：存放在 Git 版本控制系統，每次修復經 `clasp push` 後下 `git tag`。
2. **Script Properties 備份**：
   - 將包含 `SPREADSHEET_ID`, `ADMIN_USERNAME`, `PASSWORD_SALT`, `PASSWORD_HASH`, `SESSION_SECRET` 之 Key 名稱集中於密碼管理器（如 1Password / Keepass）維護。

---

## 2. 測試環境還原與演練程序 (Restore Procedure)

### 2.1 複製備份至 TEST 環境
1. 開啟最新一份備份試算表，點選「檔案 ➔ 建立副本」，重新命名為 `Futain_Test_Spreadsheet_Restore_Test`。
2. 取得該還原副本之 `SPREADSHEET_ID`。

### 2.2 設定與連結測試腳本
1. 開啟 TEST GAS 腳本，進入「專案設定 ➔ 指令碼屬性」。
2. 將 `SPREADSHEET_ID` 更新為還原副本之 ID。

### 2.3 執行一致性核對驗證
開啟 `ManualTests.gs`，執行下列測試函式以完成復原驗證：

```javascript
// 1. 擴充結構校驗
setupSpreadsheet();

// 2. 一致性與狀態機核對演練
testPhase003ConsistencyAndSecurity();
```

---

## 3. 實例復原演練紀錄 (Mock Disaster Recovery Log)

| 演練日期 | 演練型態 | 還原來源檔名 | 核對結果 | 測試執行者 | 備註 |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 2026-07-22 | 災難復原演練 | `Futain_Test_Spreadsheet_20260721` | ✅ PASS (8/8 驗收通過) | AI Pair / Admin | 備份還原花費時間 3 分鐘，資料庫結構與大寫狀態一致性完好 |

---

## 4. 遷移失敗與緊急回復方案 (Rollback Plan)

若部署新版本 GAS Web App 後發現重大異常：

1. 開啟 GAS 編輯器，進入「部署 ➔ 管理部署」。
2. 選擇「編輯」➔ 將版本切換回「上一版穩定 Version (如 Version 3)」。
3. 點選「儲存」，幾秒內即可無縫將線上 Web App 還原至升級前版本。
