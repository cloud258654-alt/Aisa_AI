# 福田貨櫃倉儲出租系統 — 管理員部署與維護手冊 (Deployment Manual)

- **版本**：v1.0.0
- **適用對象**：系統維護人員、DevOps、IT 管理員

---

## 🛠️ 一、後端 (GAS) 部署 SOP

### 1. 建立獨立 Google Spreadsheet
- 建立 `TEST` 與 `PRODUCTION` 兩份獨立試算表，記錄其 `SPREADSHEET_ID`。

### 2. 設定 Script Properties
進入 GAS 專案設定 ➔ 指令碼屬性，設定 6 大必備變數：

```text
SPREADSHEET_ID = [Spreadsheet ID]
ADMIN_USERNAME = admin
PASSWORD_SALT = [Salt]
PASSWORD_HASH = [SHA-256 Hash]
SESSION_SECRET = [強 Secret]
SESSION_TTL_SECONDS = 86400
```

### 3. 初始化試算表與白名單驗證
- 執行 `Setup.gs` 之 `setupSpreadsheet()` 初始化 14 張工作表。
- 執行 `ManualTests.gs` 之 `testPhase003ConsistencyAndSecurity()`。

### 4. 發布 Web App 部署
- 新增部署 ➔ Web 應用程式 ➔ 執行身份設為「我」，誰可以存取設為「所有人 (Anyone)」。

---

## 💻 二、前端 (React Vite PWA) 建置 SOP

1. 設定 `container-rental-app-v1/.env.local` 之 `VITE_GAS_WEB_APP_URL`。
2. 執行自動化檢查與打包：
   ```bash
   npm ci
   npm run lint
   npm run test
   npm run build
   ```
3. 將 `dist/` 部署至靜態網站託管平台。
