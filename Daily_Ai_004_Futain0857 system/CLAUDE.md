# 貨櫃出租系統開發指引

本目錄的主要產品為 `container-rental-app-v1`，以 React/Vite、Google Apps Script Web App 與 Google Sheets 提供貨櫃、客戶、租約與帳務營運管理。本系統無獨立的實體 HTTP 後端，Firebase 與 Firestore 已完全移除。

## 架構與技術棧

- **前端**：React + Vite + TypeScript + Tailwind CSS (RWD / PWA)。
- **後端**：Google Apps Script (GAS) Web App，所有操作統一使用 POST (`Content-Type: text/plain;charset=utf-8`)。
- **資料儲存**：Google Drive 中的 Google Sheets 試算表（包括分頁：`customers`, `containers`, `rental_records`, `customer_ledgers`, `management_ledgers`, `audit_logs`）。
- **驗證方式**：單一管理員帳號密碼登入。後端使用雜湊與鹽值比對，簽發具有時效且含簽章的 Session Token 儲存於前端 `sessionStorage`。

## 目錄結構說明

- `apps-script/`：Google Apps Script 後端程式碼。
- `container-rental-app-v1/src/services/api/gasClient.ts`：與 GAS Web App 進行通訊的共用 Client 端，自動處理 302 重導向與 Session Token 注入。
- `container-rental-app-v1/src/services/api/`：API 呼叫抽象層（均重導向至 `callGasApi`）。
- `container-rental-app-v1/src/contexts/SessionContext.tsx`：管理管理員 Session 登入狀態與過期檢測。
- `container-rental-app-v1/project_management/`：系統架構、部署手冊與 API 規格文件。

## 開發指令

在 `container-rental-app-v1` 目錄下執行：
- `npm ci`：安裝相依套件。
- `npm run lint`：程式碼風格檢查。
- `npm run test`：執行 Vitest 單元與邏輯測試。
- `npm run build`：專案編譯打包（編譯前請確保 `.env` 中的 `VITE_GAS_WEB_APP_URL` 已正確設定）。

每次功能變更後，必須更新 `project_management/CHANGELOG.md`。
