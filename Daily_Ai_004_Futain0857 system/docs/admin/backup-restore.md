# 福田貨櫃倉儲出租系統 — 備份與復原處置手冊 (Backup & Restore)

- **版本**：v1.0.0

---

## 1. 備份機制
- **備份頻率**：每日凌晨 03:00 (Asia/Taipei)。
- **方法**：於 Google Drive 自動建立正式試算表副本，命名為 `Futain_Production_Spreadsheet_YYYYMMDD`。
- **保留天數**：保留 30 天滾動副本，每月 1 號保存備份。

## 2. 還原程序
1. 複製備份試算表副本至 TEST 環境。
2. 更改 TEST GAS 的 `SPREADSHEET_ID` 指向該還原副本。
3. 執行 `setupSpreadsheet()` 與 `testPhase003ConsistencyAndSecurity()` 完成核對演練。
