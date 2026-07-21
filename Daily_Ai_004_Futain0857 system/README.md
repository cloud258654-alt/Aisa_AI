# 富田貨櫃出租營運管理系統 (Futain Container Rental SaaS System)

![Version](https://img.shields.io/badge/version-1.0.0--rc1-gold.svg)
![Status](https://img.shields.io/badge/status-Release--Candidate-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)

本專案為一套針對貨櫃出租業務設計的全方位營運管理系統。採用 **React 18 + Vite** 作為前端介面，搭配 **Google Apps Script (GAS) Web App** 與 **Google Sheets** 作為雲端 Serverless 後端與資料庫。

---

## 🌐 🚀 Live Demo & 快速體驗

### 1. 本機即時 Live Demo (Local Live Preview)
如果本機 Vite 開發伺服器已在運行中，請點擊下方連結造訪：

👉 **[開啟 Live Demo 應用程式 (http://localhost:5173/)](http://localhost:5173/)**

### 2. 一鍵快捷試用登入 (Quick Demo Login)
在登入頁面中，點選金黃色按鈕即可一鍵進入系統測試：

- **快捷登入按鈕**：`🚀 本機測試：點我一鍵快捷登入 (免密碼 - TEST ONLY)`
- **測試管理員帳號**：`admin`
- *(註：一鍵快捷登入為 TEST/DEV 測試專用，正式 Production 建置模式下將自動隱藏)*

### 3. 線上靜態預覽部署 (Live PWA Deployment)
您可以將產出之 `container-rental-app-v1/dist/` 目錄直接部署至 Vercel, Netlify 或 GitHub Pages 作為展示平台：

```bash
cd container-rental-app-v1
npm run build
# 靜態打包檔案將產出於 dist/ 目錄，支援 PWA 離線快取
```

---

## 🌟 系統核心特色 (Key Features)

- 🎨 **深藍與金色頂級 SaaS 視覺設計**：具備深藍 (`#071B4A`) 與金黃色調高對比設計、15+ 向量 SVG 圖示，替代傳統 Emoji。
- 📦 **多櫃合約與價格快照**：支援單一合約關聯多個貨櫃、自訂費率方案與起租/退租流程。
- 💰 **應收分期與多管道對帳**：支援租金分期帳單、押金帳單、部分付款入帳與作廢紀錄。
- 🔄 **7 步驟退租 Wizard**：引導遙控器與配件清點、損壞與清潔費扣抵試算、貨櫃狀態恢復 `AVAILABLE`。
- 🛡️ **資料一致性與資安防護**：Canonical 狀態正規化、`StateMachine.gs` 預檢白名單、`LockService` 撞櫃鎖、`requestId` 寫入冪等防護。
- 📊 **UTF-8 BOM CSV 報表匯出**：客戶、貨櫃、合約、帳單、付款與營運支出等 6 類 CSV 報表匯出，Excel 打開中文無亂碼。
- 📱 **PWA 響應式支援**：支援桌機 (1440px)、平板 (768px) 與手機 (390px) 響應式體驗，並提供離線防誤存警示。

---

## 📁 交付與驗收文檔索引

- 📘 [快速入門指南 (Quick Start)](docs/user/quick-start.md)
- 📖 [使用者完整操作手冊 (User Manual)](docs/user/user-operation-manual.md)
- 🛠️ [管理員部署與維護手冊 (Deployment Manual)](docs/admin/deployment-manual.md)
- 💾 [備份與還原處置手冊 (Backup & Restore)](docs/admin/backup-restore.md)
- 📋 [30 項 UAT 驗收測試矩陣 (UAT Test Cases)](docs/acceptance/customer-acceptance-test.md)
- 🚦 [Production 部署門禁審查表 (Production Gate Checklist)](docs/acceptance/production-gate-checklist.md)
- 🏷️ [Release Candidate Notes v1.0.0-rc1](docs/release/release-notes-v1.0.0-rc1.md)

---

## 💻 本機開發與建置步驟

```bash
# 1. 進入前端專案目錄
cd container-rental-app-v1

# 2. 安裝套件
npm ci

# 3. 啟動開發伺服器
npm run dev

# 4. 執行 ESLint 程式碼檢查
npm run lint

# 5. 執行 Vitest 單元測試
npm run test

# 6. 執行生產模式打包
npm run build
```
