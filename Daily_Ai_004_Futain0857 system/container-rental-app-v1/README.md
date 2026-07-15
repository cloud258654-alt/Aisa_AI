# 貨櫃出租營運管理系統

React/Vite 前端應用程式，使用 Google Apps Script (GAS) Web App 作為後端，並以 Google Sheets (試算表) 作為雲端資料庫，管理客戶、貨櫃、租約、帳單流水及營運支出。

## 系統架構

- **前端**：React / Vite / TypeScript / Tailwind CSS / PWA 離線檢視。
- **後端**：Google Apps Script Web App，基於 `Code.gs` 分發 POST JSON 請求。
- **資料儲存**：Google Drive 中的 Google Sheets 試算表（共 6 個分頁）。
- **驗證機制**：管理員單一帳號密碼登入驗證（後端雜湊），簽章 Token 自動管理 Session。

## 本機啟動

1. 建立 Google Sheets 試算表並建立 Apps Script 專案。
2. 貼入 `apps-script/` 程式，設定 Script Properties 後執行 `setupSpreadsheet` 初始化試算表結構並部署為 Web App。
3. 複製 `container-rental-app-v1/.env.example` 成 `.env.local`（或 `.env`），填入您的 Web App 網址：
   ```env
   VITE_GAS_WEB_APP_URL=https://script.google.com/macros/s/AKfycby.../exec
   ```
4. 執行以下指令啟動：

```bash
npm ci
npm run dev     # 啟動開發伺服器
npm run lint    # 風格檢查
npm run test    # 執行單元與邏輯測試
npm run build   # 編譯打包為 PWA 靜態檔案
```

詳細的部署與設定步驟請參考 [apps-script/README.md](file:///e:/Ai%20study/Aisa_AI/Daily_Ai_004_Futain0857%20system/apps-script/README.md) 及 [project_management/DEPLOYMENT.md](file:///e:/Ai%20study/Aisa_AI/Daily_Ai_004_Futain0857%20system/container-rental-app-v1/project_management/DEPLOYMENT.md)。
