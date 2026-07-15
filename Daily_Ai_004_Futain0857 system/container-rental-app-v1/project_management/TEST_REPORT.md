# 貨櫃出租 App V1 - 系統功能測試與驗收報告 (TEST_REPORT.md)

本測試報告記錄系統在完成 **Google Apps Script Web App 與 Google Sheets 試算表遷移** 之後的完整功能與安全驗收結果。

---

## 1. 測試環境與配置 (Test Settings)
- **測試環境**：Vite 開發伺服器 (`http://localhost:5173`) 與生產編譯打包 (`dist/`)
- **模擬載具**：Chrome 桌面版、iOS Safari 及 Android 行動版網頁
- **後端與資料庫**：Google Apps Script Web App (POST text/plain) 及 Google Sheets 試算表資料庫。

---

## 2. 自動化測試結果 (Vitest Automated Tests)

專案已配置標準的 Vitest 單元測試，排除已停用的 Firestore 規則測試，聚焦於前端計算邏輯、API 解析以及 Session 處理。

### 2.1 執行本地 Vitest 單元測試
測試套件 `tests/gasApiAndSession.test.ts` 與 `tests/dashboardCalculations.test.ts` 包含以下驗證：
* **Dashboard Math 計算**：驗證總出租率（排除停用櫃）、當月租金已收、未收租金、押金餘額（deposit_in - deposit_out）與 30 天內即將到期合約數量計算。
* **GAS API 回應解析**：測試 `gasClient` 能正常處理 `{ ok: true, data: ... }` 及 `{ ok: false, error: ... }`。
* **Session 過期處理**：模擬 Token 到期，確保前端能清除 sessionStorage，發送 `session-expired` 全域事件並引導至登入頁。
* **網路連線失敗與異常**：模擬 fetch 發生 network error 斷網，回傳標準的繁體中文提示訊息。

---

## 3. 人工功能驗收查核表 (Manual Testing Checklist)

| 功能模組 | 測試步驟 | 驗收結果 | 詳細描述 |
| :--- | :--- | :---: | :--- |
| **管理者驗證** | 輸入管理員帳號與密碼，點選登入 | **[通過 (PASS)]** | 帳密錯誤或鎖定時回傳一致的錯誤提示；成功時簽發 HMAC-SHA256 Token 寫入 `sessionStorage`。 |
| **Session 登出** | 點選 Layout 左下角或右上角「安全登出」 | **[通過 (PASS)]** | 清除本地會期暫存，前端定向回 LoginPage，後端同步註銷。 |
| **新增客戶** | 於「客戶管理」輸入姓名與電話存檔 | **[通過 (PASS)]** | 在後端 `customers` 試算表自動新增一列並生成 `CUST-YYYYMMDD-XXXX` 格式識別碼。 |
| **新增貨櫃** | 於「貨櫃管理」輸入貨櫃編號及存放位置存檔 | **[通過 (PASS)]** | 在後端 `containers` 試算表新增該筆貨櫃列，預設狀態為 `available`。 |
| **建立租約 (防呆)** | 1. 建立合約，自動簽發押金與首月帳單明細<br/>2. 對已被承租的貨櫃嘗試重複簽約 | **[通過 (PASS)]** | 1. 成功在 `rental_records` 建立合約，在 `customer_ledgers` 自動寫入押金與租金應收，貨櫃狀態在 lock 保護下自動改為 `rented`。<br/>2. 重複出租時，後端 Script Lock 中檢測失敗，拋出「貨櫃出租中不可承租」錯誤，交易回滾。 |
| **登記客戶付款** | 對 unpaid 帳單點選「登記收款」，輸入入帳日 | **[通過 (PASS)]** | 成功修改該帳單狀態為 `paid`，並回填付清日期與收據編號。 |
| **營運支出登記** | 輸入廠商名稱與金額，選擇是否「資本化」 | **[通過 (PASS)]** | 成功記錄於 `management_ledgers`。資本化項目不計入當期純費用損益。 |
| **辦理退租** | 對生效合約點選「辦理退租」，輸入退租日 | **[通過 (PASS)]** | 在 Script Lock 保護下，合約狀態改為 `ended`，並自動將對應貨櫃狀態恢復為 `available`，寫入審計日誌。 |
| **離線限制寫入** | 斷開網路連線，進入系統畫面 | **[通過 (PASS)]** | 畫面上方與側邊欄顯示黃色「離線狀態」提示；所有「新增」、「編輯」、「標記付款」、「辦理退租」等變更按鈕均轉為 **Disabled** 禁用狀態，唯讀顯示快取數據，防止 Sheets 資料寫入衝突。 |
| **CSV 資料匯出** | 於各列表點選「匯出 CSV」 | **[通過 (PASS)]** | 成功下載檔案，內含 UTF-8 BOM，Excel 開啟不亂碼。 |
