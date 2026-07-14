# Container Rental Production Readiness Phase 1

## 摘要

已完成 Auth Profile/角色架構、最小權限 Firestore Rules、環境變數 Firebase 初始化、測試與 CI。新增 `userProfile`、Auth Context、PermissionGuard、純 Dashboard 計算、單元測試、Rules 測試、部署文件與 CI。

## 權限矩陣

| 功能 | admin | manager | finance | staff |
|---|---|---|---|---|
| 客戶讀取/編輯 | 是/是 | 是/是 | 是/否 | 是/是 |
| 貨櫃讀取/編輯 | 是/是 | 是/是 | 是/否 | 是/限非財務欄位 |
| 租約讀取/編輯 | 是/是 | 是/是 | 是/否 | 是/否 |
| 帳務與支出 | 是/是 | 是/是 | 是/是 | 是/否 |
| users 與設定 | 是 | 否 | 否 | 否 |

## 測試與人工事項

`npm run lint`、`npm run test`、`npm run build` 與 `npm run test:rules` 的實際結果應以本次交付終端紀錄為準。人工操作：建立 Firebase 正式專案、首位 Auth/admin Profile、設定部署環境變數、部署 Rules 和網站。正式前檢查登入、角色限制、PWA、離線同步與備份/回滾流程。

## 最終驗證狀態（2026-07-14）

本 Codex 環境找不到 Node.js、npm 和 Java，故未執行 npm 安裝、lockfile 更新、lint、測試、build 或 Emulator。已修正 CI workflow 至儲存庫根目錄、加入前端按鈕/處理器權限防呆，並強化 staff 的貨櫃欄位限制；上述項目仍需在 Node 20 環境實測。
