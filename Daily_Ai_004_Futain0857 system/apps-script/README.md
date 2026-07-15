# Google Apps Script 後端部署說明

本專案使用 Google Apps Script (GAS) Web App 作為 API 後端，並將資料保存在 Google Sheets。

## 部署與設定步驟

### 1. 建立 Google 試算表 (Google Sheets)
1. 在 Google Drive 中新增一個空白試算表。
2. 複製瀏覽器網址列中的試算表 ID。例如，網址為：
   `https://docs.google.com/spreadsheets/d/1A2B3C4D5E6F7G8H9I0J/edit#gid=0`
   則 `1A2B3C4D5E6F7G8H9I0J` 即為 **Spreadsheet ID**。

### 2. 建立 Google Apps Script 專案
1. 開啟剛剛建立的試算表，點選選單中的 **「擴充功能」 ➔ 「Apps Script」**，或直接至 [Google Apps Script 官網](https://script.google.com/) 建立獨立專案。
2. 在專案中新增對應的 `.gs` 檔案（例如 `Code.gs`, `Router.gs`, `Auth.gs` 等），將 `apps-script/` 目錄下對應的程式碼內容複製貼上。
3. 新增 `appsscript.json` 內容到編輯器（若編輯器中看不到此檔案，請於左側「專案設定」中勾選「在編輯器中顯示 appsscript.json 資訊清單檔案」）。

### 3. 設定指令碼屬性 (Script Properties)
在 Apps Script 專案左側齒輪 **「專案設定」 (Project Settings)** 的 **「指令碼屬性」 (Script Properties)** 中新增以下設定：

| 屬性名稱 (Property Name) | 說明 | 範例值 |
|---|---|---|
| `SPREADSHEET_ID` | 步驟一複製的 Google Sheets 試算表 ID | `1A2B3C4D5E6F7G8H9I0J` |
| `ADMIN_USERNAME` | 管理者登入帳號名稱 | `admin` |
| `PASSWORD_SALT` | 用於密碼雜湊的隨機鹽值 | `SomeRandomSaltStringHere` |
| `PASSWORD_HASH` | 使用上述鹽值雜湊後的密碼 SHA-256 Hex 字串 | *（參考下方密碼雜湊產生法）* |
| `SESSION_SECRET` | 用於簽發 Session Token 簽章的隨機金鑰 | `YourSuperSessionSecretString` |
| `SESSION_TTL_SECONDS`| Session 登入效期秒數 (預設為 86400 秒，即 1 天) | `86400` |
| `LOGIN_MAX_FAILURES` | 連續登入失敗鎖定上限次數 (預設為 5) | `5` |
| `LOGIN_LOCK_MINUTES` | 登入鎖定時間分鐘數 (預設為 5) | `5` |

#### 🔑 管理者密碼雜湊計算方式
您可以直接在 Apps Script 編輯器中，選擇執行 `Setup.gs` 中的 `setupScriptPropertiesExample` 函式，或在主選單直接新增一個臨時的測試函式，例如：
```javascript
function generateMyHash() {
  var password = "您的管理員密碼";
  var salt = "您的PASSWORD_SALT值";
  var hash = hashPassword(password, salt);
  Logger.log("PASSWORD_HASH 應該設定為: " + hash);
}
```
執行後至下方的「執行記錄」中複製產生的 `hash` 字串，填入指令碼屬性中的 `PASSWORD_HASH`，然後刪除該臨時函式以策安全。

### 4. 初始化試算表結構
1. 在 Apps Script 編輯器的程式碼檔案清單中選擇 `Setup.gs`。
2. 在上方的執行函式下拉選單中選擇 **`setupSpreadsheet`**。
3. 點選 **「執行」 (Run)** 按鈕，並授權該專案讀寫您的 Google Sheets 權限。
4. 執行完成後，您的 Google Sheets 將會自動建立 6 個分頁並預設好欄位標頭：
   - `customers`
   - `containers`
   - `rental_records`
   - `customer_ledgers`
   - `management_ledgers`
   - `audit_logs`

### 5. 部署為 Web 應用程式 (Web App)
1. 點選右上角的 **「新部署」 (New deployment)**。
2. 點選左側齒輪選單，選取類型為 **「Web 應用程式」 (Web app)**。
3. 設定：
   - **說明**：例如 `Container Rental App Backend V1.1.0`
   - **執行身分**：選擇 **「我」 (Me)**
   - **誰可以存取**：選擇 **「任何人」 (Anyone)**
4. 點選 **「部署」 (Deploy)**。
5. 部署完成後，複製產生的 **「網頁應用程式網址」 (Web app URL)**。例如：
   `https://script.google.com/macros/s/AKfycby.../exec`

### 6. 設定 React 前端
將步驟五複製的網址，寫入前端專案根目錄 `.env`（或 `.env.local`）檔案中的 `VITE_GAS_WEB_APP_URL` 變數：
```env
VITE_GAS_WEB_APP_URL=https://script.google.com/macros/s/AKfycby.../exec
```
*註：發布及編譯打包 (npm run build) 時，環境變數會被編譯進前端代碼中。*
