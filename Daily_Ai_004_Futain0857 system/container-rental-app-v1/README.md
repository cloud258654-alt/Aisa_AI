# 貨櫃出租營運管理系統

React/Vite 前端直接使用 Firebase Auth 與 Firestore 管理客戶、貨櫃、租約、客戶帳務及營運支出。`src/services/api` 是 Firestore 資料存取抽象層，並非 HTTP API；目前沒有獨立 Backend API。

## Live Demo

尚未部署。請勿將未設定環境變數的版本視為可用展示站。

## 本機啟動

複製 `.env.example` 成 `.env.local`，填入 Firebase Web App 的建置環境變數（勿提交），然後執行：

```bash
npm ci
npm run dev
npm run lint
npm run test
npm run build
```

啟用 Firebase Console 的 Email/Password 後，建立第一位 Auth 使用者及 `users/{uid}` admin Profile；缺 Profile 或 `status: disabled` 的帳號會被拒絕。部署前依 `project_management/DEPLOYMENT.md` 建立正式專案、部署 Rules 並驗證角色。Firestore 離線快取只會在 App 執行時於網路恢復後同步。
