# 正式部署流程

1. 建立 Firebase Production Project，啟用 Email/Password Authentication。
2. 在 Console 建立第一位 Auth 使用者；以其 UID 建立 `users/{uid}`，填入 email、display_name、`role: admin`、`status: active` 與時間欄位。
3. 於部署平台設定所有 `.env.example` 的 `VITE_FIREBASE_*` 值；不可提交 `.env` 或 service account。
4. 在 Node 20 與 Java 可用的部署環境先執行 `npm install`（更新並提交 lockfile）、`npm ci`、`npm run check`、`npm run test:rules`，再以 `firebase deploy --only firestore:rules` 部署規則。
5. 執行 `npm run build`，Firebase Hosting 可使用 `firebase.json` 的 `dist` 設定；也可將同一產物部署 Vercel。
6. 上線後驗證登入、admin/manager/finance/staff 權限、PWA 安裝、離線寫入及網路恢復後同步。
7. 回滾時先停止前端發布，還原前一個 Hosting/Vercel deployment，並從版控中已驗證的 `firestore.rules` 重新部署；資料復原應依 Firestore 匯出備份進行。
