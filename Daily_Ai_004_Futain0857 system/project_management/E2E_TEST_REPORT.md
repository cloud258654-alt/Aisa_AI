# 福田貨櫃倉儲出租系統 — TEST 環境端到端真實 E2E 驗證報告 (E2E_TEST_REPORT.md)

- **驗證環境**：TEST 測試環境 (獨立隔離 Google Spreadsheet)
- **測試日期**：2026-07-22
- **驗證人員**：系統管理員 / AI Pair
- **整體結果**：`TEST_E2E_ALL_PASSED`

---

## 🔄 一、完整端到端 16 步驟流程實測

```text
[1. 管理員登入] ➔ [2. 新建客戶] ➔ [3. 新建貨櫃庫存] ➔ [4. 設定費率方案]
       │
       ▼
[5. 啟用多櫃合約] ➔ [6. 產出押金與分期帳單] ➔ [7. 應收對帳與部分付款] ➔ [8. 完成全額付款]
       │
       ▼
[9. 辦理合約續約] ➔ [10. 啟動退租結算] ➔ [11. 遙控器清點與扣款] ➔ [12. 貨櫃驗收解鎖 AVAILABLE]
       │
       ▼
[13. 登記營運支出] ➔ [14. 匯出 6 類 CSV 報表] ➔ [15. 查看 Audit 稽核] ➔ [16. 儀表板動態更新]
```

### 詳細實測紀錄：

| 步驟 | 測試項目 | 實測操作與輸入資料 | Sheets 工作表對應 | 驗收結果 |
| :---: | --- | --- | --- | :---: |
| **1** | 管理員登入 | 輸入管理員帳號與密碼 HMAC 簽章驗證 | `session_logs` | ✅ `PASS` |
| **2** | 新建客戶 | 新建「福田企業 (CUST-20260722-001)」 | `customers` | ✅ `PASS` |
| **3** | 新建貨櫃 | 新建「CONT-A01 (20呎)」與「CONT-A02 (20呎)」 | `containers` (狀態: `AVAILABLE`) | ✅ `PASS` |
| **4** | 設定費率 | 新設「20呎年租優惠方案 (48,000/年, 押金 5,000)」 | `rate_plans` | ✅ `PASS` |
| **5** | 啟用多櫃合約 | 建立含 CONT-A01 與 CONT-A02 之 2 櫃合約 | `contracts`, `contract_items` | ✅ `PASS` (貨櫃自動轉 `RENTED`) |
| **6** | 產出應收帳單 | 系統自動產出租金分期帳單與押金帳單 | `invoices` (狀態: `UNPAID`) | ✅ `PASS` |
| **7** | 部分對帳付款 | 登記部分付款 $10,000 元 | `payments`, `invoices` | ✅ `PASS` (帳單轉 `PARTIAL`, 餘額對加) |
| **8** | 完成全額付款 | 結清剩餘尾款 $14,000 元 | `payments`, `invoices` | ✅ `PASS` (帳單轉 `PAID`, 餘額歸零) |
| **9** | 辦理合約續約 | 為到期合約辦理續約關聯手續 | `contracts` (新舊合約鏈結) | ✅ `PASS` |
| **10** | 啟動退租結算 | 開啟 7 步驟退租 Wizard 啟動結算 | `termination_records` | ✅ `PASS` (合約 `ENDING`, 貨櫃 `INSPECTION`) |
| **11** | 遙控器清點扣款 | 清點遙控器與損壞扣款試算 | `termination_records`, `invoices` | ✅ `PASS` (押金扣抵與餘額試算) |
| **12** | 貨櫃驗收解鎖 | 現場檢查 passed，完成退租驗收 | `containers` | ✅ `PASS` (貨櫃解鎖恢復 `AVAILABLE`) |
| **13** | 登記營運支出 | 登記 7 月份地租與場地雜支 $15,000 元 | `management_ledgers` | ✅ `PASS` |
| **14** | 匯出 6 類 CSV | 下載客戶、貨櫃、合約、帳單、付款、支出報表 | 前端 CSV 工具 | ✅ `PASS` (UTF-8 BOM Excel 中文無亂碼) |
| **15** | 稽核紀錄防護 | 查看 Audit Log 異動軌跡 | `audit_logs` | ✅ `PASS` (禁止直接 CRUD 寫入) |
| **16** | 儀表板動態更新 | 儀表板即時計算出租率、實收與待催收欠款 | `DashboardService` | ✅ `PASS` |

---

## 🔒 二、安全、併發與狀態機真實驗證

1. **併發撞櫃防護**：模擬 2 個視窗同時承租同一空櫃，第 2 個請求被 `LockService` 排他鎖阻擋。
2. **`requestId` 冪等性**：使用相同 `requestId` 提交重複付款，第 2 次請求獲得快取結果，未重複扣款。
3. **Session 到期阻擋**：模擬 Token 過期後呼叫 API，系統傳回 `UNAUTHORIZED` 並跳轉登入頁。
4. **非法狀態變更阻擋**：嘗試直接將 `RENTED` 貨櫃改為 `AVAILABLE`，被後端 `StateMachine.gs` 白名單預檢阻擋。
5. **Audit Log 保護**：嘗試直接修改 `audit_logs` 工作表，被 `Router.gs` 拒絕並傳回 `UNAUTHORIZED`。

---

## 📱 三、PWA 安裝與離線阻擋驗證

- **Manifest & Service Worker**：`manifest.webmanifest` 與 `sw.js` 成功預快取 6 個核心靜態資源。
- **離線寫入阻擋**：當離線時，前端按鈕跳出「⚠️ 目前離線，請恢復網路連線後再進行儲存/異動」黃色通知彈窗，阻止誤觸發。

---

## 💾 四、備份與還原實測結果

- 複製 TEST 試算表測試副本，將 ID 填入 TEST `ScriptProperties` 後執行 `setupSpreadsheet()` 與 `testPhase003ConsistencyAndSecurity()`，資料庫結構與大寫 Canonical 狀態完整復原。
