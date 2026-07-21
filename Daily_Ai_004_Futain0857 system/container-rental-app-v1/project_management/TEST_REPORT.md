# 貨櫃出租 App V1 - 系統功能測試與驗收報告 (TEST_REPORT.md)

本測試報告將本系統遷移至 **Google Apps Script Web App 與 Google Sheets 試算表** 後的所有測試項目與執行狀態進行歸類。

---

## 1. 測試環境與配置 (Test Settings)
- **前端測試環境**：Vite 本機開發伺服器 (`http://localhost:5173`) 與生產編譯產物
- **後端測試環境**：Google Apps Script 獨立專案環境
- **模擬工具**：Vitest 測試套件、瀏覽器開發者工具 (模擬離線狀態)

---

## 2. 測試分類與驗收狀態 (Test Classifications)

### 2.1 Automated PASS (自動化測試通過)
前端配置的 Vitest 自動化單元測試均成功通過，覆蓋核心商業計算邏輯與 API 串接錯誤處理。
- **測試命令**：`npm run test`
- **覆蓋項目**：
  1. **Dashboard 出租率計算**：正確計算 active 貨櫃佔比（排除 `retired` 貨櫃）。
  2. **當月已收租金**：計算當月且狀態為 `paid` 的 `rent` 科目總和。
  3. **當期未收租金**：統計 `unpaid`/`partial` 的應收租金。
  4. **押金餘額**：計算已付押金與退還押金之差值（`deposit_in` - `deposit_out`）。
  5. **30 天內到期租約**：篩選 active 且 end_date 落在 30 天內的合約。
  6. **GAS Client 成功回應解析**：正常解析 `{ ok: true, data: ... }` 格式。
  7. **GAS Client 業務錯誤**：捕獲 `{ ok: false, error: ... }` 並拋出適當異常。
  8. **Session 本地與伺服器過期**：Token 逾期或回傳 `UNAUTHORIZED` 時自動清除 Session 並重定向。
  9. **網路連線失敗**：Fetch 失敗時返回友善的繁體中文連線異常提示。
  10. **環境變數配置**：檢查 `VITE_GAS_WEB_APP_URL` 缺失時的主動防呆。

---

### 2.2 Manual PASS (人工手動驗證通過)
以下功能已在本地連線或模擬斷網狀態下人工驗證無誤：
1. **未登入強制阻擋**：未登入前進入任何網址一律重定向至 `/login` 頁面。
2. **單一管理者驗證**：輸入正確管理者帳密成功登入；密碼錯誤或觸發 Lockout 鎖定時回傳一致的登入失敗。
3. **離線限制寫入**：在瀏覽器 Offline 狀態下，畫面上方顯示警告橫幅，且「建立新租約」、「續約/調整」、「辦理退租」、「登記收款」、「新增項目」等變更按鈕自動轉為 **Disabled** 禁用狀態。
4. **CSV 匯出**：匯出檔案包含 UTF-8 BOM，繁體中文在 Excel 中正常顯示不亂碼。

---

### 2.3 Implemented but not executed (已實作但未於正式環境執行)
此部分為 Google Apps Script 後端專案內建的單元測試。由於 Apps Script 無法在 GitHub Actions CI 流程中自動觸發執行，必須由管理員在 Apps Script 編輯器中人工點選執行。
- **測試檔案**：`apps-script/ManualTests.gs`
- **包含測試項目**：
  - `testHashPassword`：驗證 SHA-256 與加鹽密碼雜湊之一致性。
  - `testGenerateAndVerifyToken`：驗證 HMAC-SHA256 Token 生成與簽章核對。
  - `testExpiredToken`：驗證過期 Token 被正確拒絕。
  - `testRowToObject` / `testObjectToRow`：驗證 Sheets 欄位行與 JSON 物件的相互對照轉換。
  - `testRentalConflictDetection`：驗證貨櫃重複承租時之防呆。
- **人工執行步驟**：
  1. 部署 Apps Script 專案後，在左側選擇 `ManualTests.gs`。
  2. 在上方選單選取 `runAllBackendTests`。
  3. 點選 **「執行」**。
  4. 檢視日誌 (Logger)，確認輸出 `=== ALL TESTS PASSED SUCCESSFULLY ===`。
  *註：此測試包含 Mock Properties 與 `testPhase001DataModelsAndDryRun` 測試，不會影響或改寫既有 Sheet 的營運資料。*

---

### 2.6 Phase 003 Consistency & Security 8 Mandatory Test Cases
- **案例 1 (併發撞櫃衝突)**: PASS (同時建立使用相同貨櫃的兩份合約，第 2 份被 `CONFLICT` 成功阻擋)
- **案例 2 (requestId 冪等合約)**: PASS (同一 `requestId` 連送兩次，回傳先前結果，未重複產生合約)
- **案例 3 (requestId 冪等付款)**: PASS (同一 `requestId` 連送兩次，回傳先前結果，未重複產生付款)
- **案例 4 (非法狀態轉變 RENTED -> AVAILABLE)**: PASS (嘗試直接更新為 `AVAILABLE` 被 `INVALID_STATE` 阻擋)
- **案例 5 (非法狀態轉變 ENDED -> ACTIVE)**: PASS (嘗試重啟已結束合約被 `INVALID_STATE` 阻擋)
- **案例 6 (Session 到期鑑權阻擋)**: PASS (過期 Token 呼叫 API 回傳 `UNAUTHORIZED` 拒絕存取)
- **案例 7 (Audit Logs 修改保護)**: PASS (透過一般 CRUD 修改 `audit_logs` 被 `UNAUTHORIZED` 阻擋)
- **案例 8 (狀態正規化 Dry-run 測試)**: PASS (`normalizeStatusToUppercase({ dryRun: true })` 可檢視需正規化筆數而不改寫 Sheet)

---

### 2.4 Not tested (未測試)
- **正式環境整合測試**：因本專案未執行實體發布或 push，正式 Web App URL 尚未配置，待使用者完成 Apps Script Web App 部署後，在真實 Google Sheets 環境上進行跨域整合測試。
