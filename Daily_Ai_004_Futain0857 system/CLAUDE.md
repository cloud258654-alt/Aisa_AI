# 貨櫃出租系統開發指引

本目錄的主要產品為 `container-rental-app-v1`，以 React/Vite、Firebase Auth 與 Firestore 提供貨櫃、客戶、租約與帳務營運管理；沒有獨立 HTTP Backend。

## 架構與目錄

- `src/services/api` 是 Firestore 資料存取抽象層，不是 HTTP API。
- `src/services/firebase` 初始化 Firebase；設定只來自 `VITE_FIREBASE_*` 環境變數。
- `src/services/auth` 與 `src/contexts/AuthContext.tsx` 管理登入者的 Profile。
- `src/types` 是資料合約；不可任意改名 Collection 或既有欄位。
- `project_management` 為部署、架構與測試交接文件。

Firestore Collections 為 `users`、`customers`、`containers`、`rental_records`、`customer_ledgers`、`management_ledgers`。其中前五個營運集合加上 `management_ledgers` 均受 `firestore.rules` 保護。

## Auth、角色與資料規範

Firebase Auth Email/Password 登入後必須讀取 `users/{uid}`。Profile 欠缺或 `disabled` 必須拒絕進入；首位 admin 由 Firebase Console 建立 Auth 使用者與對應 Profile。角色是 `admin`、`manager`、`finance`、`staff`；前端僅做 UX 防呆，Firestore Rules 是實際授權邊界。

建立租約必須以 Transaction 讀取貨櫃、確認 `available`、新增 `rental_records`、更新貨櫃為 `rented`，並可同時建立首期帳務。刪除採軟刪除（`deleted_at`）；僅 admin/manager 可改變該欄位。不得新增真實憑證、提交 `.env`、`.env.local` 或 service-account 金鑰。

## 指令與紀錄

在 `container-rental-app-v1` 執行：`npm ci`、`npm run lint`、`npm run test`、`npm run build`，Rules 測試使用 `npm run test:rules`。每次功能變更後必須更新 `project_management/CHANGELOG.md`。
