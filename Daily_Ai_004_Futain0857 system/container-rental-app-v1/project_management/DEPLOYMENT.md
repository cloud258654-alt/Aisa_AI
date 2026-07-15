# 貨櫃出租 App V1 - 正式人工部署指南 (Deployment)

本系統無需配置任何獨立伺服器或 Firebase 資源，完全部署在 Google Apps Script (後端) 與靜態代管平台（前端，如 Vercel 或 GitHub Pages）。

---

## 1. 後端 Google Apps Script 部署步驟

### 1.1 建立與初始化試算表
1. 在 Google Drive 中建立一個新的 Google Sheets 試算表。
2. 複製試算表網址中的 ID（即網址 `/d/` 與 `/edit` 之間的那串 44 字元隨機字串）。
3. 點選試算表功能選單中的 **「擴充功能」 ➔ 「Apps Script」**，開啟編輯器。

### 1.2 貼入程式碼
1. 將 `apps-script/` 目錄下的所有 `.gs` 檔案貼入 Apps Script 編輯器中。
2. 將 `apps-script/appsscript.json` 複製覆蓋專案設定中的同名檔案。

### 1.3 配置 Script 屬性與密碼雜湊
1. 在 Apps Script 左側齒輪 **「專案設定」** 中，滾動到 **「指令碼屬性」**，點選新增屬性：
   * `SPREADSHEET_ID`: 剛剛複製的試算表 ID。
   * `ADMIN_USERNAME`: 管理者登入帳號（如 `admin`）。
   * `PASSWORD_SALT`: 自訂隨機安全鹽值。
   * `SESSION_SECRET`: 自訂 Session Token 簽章秘密金鑰。
2. **產生密碼雜湊值**：
   在編輯器中選擇並執行 `Setup.gs` 中的 `setupScriptPropertiesExample`，或在編輯器中新增並執行以下臨時函式：
   ```javascript
   function generateMyHash() {
     var password = "自訂管理員密碼";
     var salt = "剛剛設定的 PASSWORD_SALT";
     Logger.log("PASSWORD_HASH: " + hashPassword(password, salt));
   }
   ```
   執行後從日誌複製對應的 `PASSWORD_HASH` 十六進位字串，填入指令碼屬性中的 `PASSWORD_HASH`，然後將此臨時函式刪除。

### 1.4 初始化試算表分頁與欄位
1. 在編輯器頂部下拉選單選擇 `setupSpreadsheet` 函式。
2. 點選 **「執行」 (Run)**，並在出現權限授權提示時，核准試算表的讀寫權限。
3. 執行完畢後，開啟 Google Sheets，確認 6 大分頁（`customers`、`containers` 等）已自動建立且首列欄位已凍結。

### 1.5 發布為 Web 應用程式 (Web App)
1. 點選編輯器右上角 **「新部署」 (New deployment)**。
2. 點選左側齒輪，選擇部署類型為 **「Web 應用程式」 (Web app)**。
3. 設定參數：
   * **執行身分 (Execute as)**：選擇 **「我」 (Me)**。
   * **誰可以存取 (Who has access)**：選擇 **「任何人」 (Anyone)**。
4. 點選 **「部署」 (Deploy)**，核准存取，並複製產生的 **「網頁應用程式網址」 (Web app URL)**。

---

## 2. 前端 React/Vite 部署步驟

### 2.1 環境變數設定
1. 於前端專案目錄下，複製 `.env.example` 並命名為 `.env`。
2. 填入後端部署產生的 Web App 網址：
   ```env
   VITE_GAS_WEB_APP_URL=https://script.google.com/macros/s/AKfycby.../exec
   ```
   *注意：不可將真實網址提交到 Git 儲存庫。*

### 2.2 編譯打包與發布
1. 在前端目錄下執行編譯：
   ```bash
   npm ci
   npm run lint
   npm run test
   npm run build
   ```
2. 將編譯輸出目錄 `dist/` 中的所有檔案，上傳至靜態代管平台（如 Vercel、GitHub Pages、或 Cloudflare Pages）。
3. 部署完成後，即可直接透過瀏覽器開啟前端網址，測試管理員登入及所有 CRUD 操作。
