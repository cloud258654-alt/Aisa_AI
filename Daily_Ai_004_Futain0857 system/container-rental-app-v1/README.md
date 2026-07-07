# 貨櫃出租公司營運管理系統 (Container Rental App V1) - Firebase 版

本專案是一套專為貨櫃出租營運設計的輕量級 MVP（最小可行性產品），支援手機、平板與 PC 跨平台操作，具備離線操作暫存、漸進式網頁應用（PWA）安裝以及 Firebase Firestore 雲端同步功能。

---

## 🔗 線上體驗 (Live Demo)
您可以在此開啟展示版本進行操作體驗：**[👉 點此進入首頁 Live Demo](https://your-live-demo-link.vercel.app)**

> [!NOTE]
> 線上展示版若在未配置後端 Firebase 憑證的情況下，會自動運作於本地模擬快取模式。若要將資料同步回您的 Firestore 資料庫，請依照下方指引完成 Firebase 專案建立，並在 App 內的「系統設定」頁面輸入您的 Firebase 網頁 SDK 配置資訊即可！

---

## 1. 專案目的
為現場貨櫃場地管理人員提供最便利的手機操作工具，可隨時在場地登記客戶、變更貨櫃狀態、收取租金、記錄修繕支出。系統底層進行 API 與資料型別抽象化，保留未來無縫升級至正式 PostgreSQL 資料庫或繼續擴展 Firebase 功能的路徑。

---

## 2. 技術架構
- **前端框架**：React 18 + Vite 5 + TypeScript + Tailwind CSS v3
- **本地儲存**：Firestore 本地離線持久化快取 (IndexedDB)
- **資料庫後端**：Firebase Firestore 雲端 NoSQL 資料庫
- **打包/PWA**：Vite PWA Plugin (自動產生 Service Worker 與離線 precache 快取)

---

## 3. 安裝指令

請確認已安裝 Node.js 環境（支援 Node 18 及以上版本），並在專案根目錄下執行：

```bash
# 進入前端專案目錄
cd container-rental-app-v1

# 安裝依賴套件
npm install
```

---

## 4. 啟動與打包指令

### 本地開發啟動
```bash
npm run dev
```
啟動後可在瀏覽器開啟 `http://localhost:5173`。

### 專案生產打包
由於本地 Node.js 18 環境下可能缺乏部分 global.crypto 功能導致 Rollup Terser 打包報錯，本專案已內建預加載腳本解決此問題。請執行以下指令打包：
```bash
# 執行 TypeScript 檢查與 Vite 生產打包 (內建 crypto 相容墊片)
npx tsc -b; node -r ./preload-crypto.cjs ./node_modules/vite/bin/vite.js build
```
打包產物將放置在 `dist/` 資料夾下，可直接部署至 Vercel, GitHub Pages, Netlify 或 VPS。

---

## 5. Firebase 設定與環境變數 `.env` 配置

1. 開啟 [Firebase Console](https://console.firebase.google.com/) 並建立新專案。
2. 啟用 **Cloud Firestore**（於開發階段可選擇測試模式或配置寬鬆的規則，正式生產請參考 `project_management/FIRESTORE_RULES.md`）。
3. 新增一個「網頁應用程式 (Web App)」，複製產生的 `firebaseConfig` 憑證。
4. 在前端目錄下建立 `.env` 檔案，填入您的 Firebase 憑證資訊：

```env
VITE_FIREBASE_API_KEY=your_api_key_here
VITE_FIREBASE_AUTH_DOMAIN=your_auth_domain_here
VITE_FIREBASE_PROJECT_ID=your_project_id_here
VITE_FIREBASE_STORAGE_BUCKET=your_storage_bucket_here
VITE_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id_here
VITE_FIREBASE_APP_ID=your_app_id_here

# 環境
VITE_APP_ENV=development
```

> [!TIP]
> **動態變更憑證**：
> 系統已支援在前端「系統設定 (Settings)」頁面直接輸入 Firebase 憑證金鑰，儲存後會覆蓋環境變數並立即生效，且自動儲存於瀏覽器 localStorage 中。這代表您無需重新打包，即可動態更換後端資料庫！

---

## 6. PWA 安裝與離線操作測試方式

### PWA 主畫面安裝
本系統已配置為 PWA，在支援 PWA 的瀏覽器（如 Chrome, Safari, Edge）開啟網頁後，點選安裝即可將 App 安裝至手機主畫面或電腦桌面獨立視窗執行。

### 離線測試與同步機制
1. 在 PC 端開啟 Chrome 開發者工具 (F12) ➔ 切換至 **Network** 標籤頁。
2. 將連線狀態由 Online 改為 **Offline**（或直接拔除手機/電腦網路）。
3. 前往「場地支出」，點選「登記支出費用」，填寫並儲存。
4. 系統會顯示「登記成功」。此時資料已寫入本地 IndexedDB 快取，且首頁 Dashboard、支出列表皆會即時渲染該筆資料。
5. 此時系統狀態列會顯示為「離線暫存」，且出現「有待上傳變更：1 筆」等提示資訊。
6. 將 Network 切換回 **Online**（恢復網路）。當 App 與 Firestore SDK 處於執行狀態下時，Firestore 會自動在背景與雲端完成同步，狀態列隨即更新為「連線同步」，無須點選任何手動同步按鈕。

---

## 7. 已知限制與架構安全防範 (Important Constraints)

1. **離線同步邊界**：Firestore 離線寫入會先進入本地快取。當網路恢復，且 **App/SDK 處於執行狀態時 (App is running)**，資料才會同步至雲端。
2. **原子性寫入與事務控制**：本系統在新建租約與退租等「多表關聯異動」時，使用批次寫入 (Batched Writes) 確保多筆寫入的原子性 (Atomicity)。但批次寫入**不等於交易 (Transaction)**；若寫入涉及「讀取後判斷」之核心邏輯（如：判斷貨櫃狀態是否為空櫃後才允許承租），系統在 API 層改用 `runTransaction` 進行控制，並可配合 Firestore Security Rules 來防止併發衝突。
3. **金鑰管理防範**：`localStorage` 儲存 Firebase 連線金鑰功能**僅限 Demo / 開發測試階段使用**。正式上線版本必須清除此項，並直接使用建置階段的 `.env` 環境變數或後台 API 注入，防止敏感凭證外洩。
4. **財務會計定義**：本系統為營運管理帳流水系統，提供營運決策與出租狀態分析，非正式會計報稅系統，正式申報仍需委託會計師處理。
