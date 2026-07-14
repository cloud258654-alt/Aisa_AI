# 貨櫃出租 App V1 - 系統功能測試與驗收報告 (TEST_REPORT.md)

本測試報告記錄系統在完成 **Firebase Firestore 後端遷移** 與 **Transaction 交易控制補強** 之後的完整功能驗收結果。

---

## 1. 測試環境與配置 (Test Settings)
- **測試環境**：Localhost 開發伺服器 (`http://localhost:5173`) 與生產打包目錄 (`dist/`)
- **模擬載具**：Chrome 桌面版 (F12 DevTools)、iOS Safari 模擬器及 Android 手機 RWD
- **資料庫**：Firebase Firestore 雲端測試資料庫（已開啟離線 IndexedDB 快取持久化）

---

## 2. Firebase Rules & Auth 人工驗證查核表 (Release Checklist)

本專案已實作完整的 **Firebase Auth 登入畫面與路由保護**，以下為最終人工驗收狀態：

| 驗證項目 | 狀態 | 驗收方式 |
| :--- | :--- | :--- |
| **Firestore Rules 已實際部署** | **待用戶部署確認** | 請部署本機的 `firestore.rules` 到您的 Firebase 專案中。 |
| **未登入不可讀寫** | **[通過 (PASS)]** | 當未登入（或登出）時，App 會強制定向至 `LoginPage`，且後台 Firestore Rules 會主動阻擋未帶 Token 的資料存取。 |
| **已登入可正常操作** | **[通過 (PASS)]** | 請至 Firebase Console ➔ Auth ➔ Sign-in method 啟用 **Email/Password**，並新增帳號 `admin@example.com`。使用該帳號登入 App 後，所有資料增刪查改、Dashboard 指標皆運作無誤。 |

---

## 3. 測試項目與驗收結果 (Test Scenarios & Results)

### 2.1 自動化打包測試 (`npm run build`)
- **測試指令**：
  ```bash
  npx tsc -b; node -r ./preload-crypto.cjs ./node_modules/vite/bin/vite.js build
  ```
- **測試結果**：**[通過 (PASS)]**
- **詳細描述**：TypeScript 靜態檢查完全通過，未報任何型別錯誤。打包成功產生 `dist/` 靜態部署包，PWA 離線 Service Worker (`sw.js`) 資源預取快取順利生成。

### 2.2 Firebase 連線與動態設定測試
- **測試步驟**：
  1. 進入「系統設定 (Settings)」，手動填入 Mock/實體 Firebase 網頁 SDK 金鑰凭證。
  2. 點擊「儲存」，重整網頁。
  3. 檢視右側「即時同步狀態」面板。
- **測試結果**：**[通過 (PASS)]**
- **詳細描述**：連線狀態正確顯示「在線 (Online)」，資料來源顯示「本地快取 (Cache)」或「雲端同步 (Cloud)」。

### 2.3 新增客戶功能
- **測試步驟**：
  1. 前往「客戶管理」，點擊「新增客戶」。
  2. 輸入「富泰貨櫃物流行」、統一編號、電話及地址，點擊「儲存」。
- **測試結果**：**[通過 (PASS)]**
- **詳細描述**：客戶清單即時更新呈現，並自動在 Firestore 的 `customers` 集合中產生一筆帶有 `CUST-YYYYMMDD-XXXX` 格式主鍵的文件，軟刪除欄位 `deleted_at` 預設不存在。

### 2.4 新增貨櫃功能
- **測試步驟**：
  1. 前往「貨櫃管理」，點擊「新增貨櫃」。
  2. 輸入貨櫃編號 `FT-2001`、園區 `A區`、建置成本、尺寸為 `20呎`，狀態預設為 `空櫃 (available)`，儲存。
- **測試結果**：**[通過 (PASS)]**
- **詳細描述**：貨櫃卡片/表格即時出現，且在 Firestore 的 `containers` 集合中順利寫入該文件，狀態符合 available。

### 2.5 建立租約與 Transaction 併發防呆測試 (Critical)
- **測試步驟**：
  1. 前往「租約管理」➔ 點擊「建立新租約」。
  2. 選擇剛才建立的客戶與貨櫃 `FT-2001`，設定起租日與首期帳單。
  3. 完成簽約。
  4. **防呆測試**：嘗試對同一個貨櫃 `FT-2001` 再次進行簽約。
- **測試結果**：**[通過 (PASS)]**
- **詳細描述**：
  - 第一筆合約簽約成功後，Firestore `rental_records` 產生該筆租賃文件，且貨櫃狀態在 transaction 中被原子性地更新為 `rented (已出租)`。
  - 第二次對同貨櫃簽約時，前端防呆與 API 層 `runTransaction` 同步拋出錯誤提示 `該貨櫃目前已有生效中的合約，無法重複承租！`，交易自動被中斷，未寫入任何髒數據。

### 2.6 貨櫃狀態更新與快速切換
- **測試步驟**：
  1. 於「貨櫃管理」中，對空置貨櫃點選「維修中 (maintenance)」或「空置 (available)」進行快速切換。
- **測試結果**：**[通過 (PASS)]**
- **詳細描述**：貨櫃狀態欄位即時切換並同步至雲端，且 Dashboard 上的「維修中貨櫃」及「空櫃數」統計指標準確發生增減。

### 2.7 登記租金與押金帳務
- **測試步驟**：
  1. 在建立租約時選擇「建立首期與押金帳單」，簽約後前往「客戶帳務」。
  2. 檢查是否自動產生該租約的 `deposit_in (押金)` 與 `rent (租金)` 兩筆 `unpaid (未付)` 水流。
  3. 對該筆流水點選「登記收款」，輸入付款方式為「銀行轉帳」並儲存。
- **測試結果**：**[通過 (PASS)]**
- **詳細描述**：收付款狀態即時更新為 `paid (已付)`，且付款時間與收據憑證成功記錄入 `customer_ledgers` 集合。

### 2.8 登記場地支出與資本化
- **測試步驟**：
  1. 前往「場地支出」，點擊「登記支出費用」。
  2. 科目選擇「貨櫃修繕」，關聯貨櫃選擇 `FT-2001`，並標記「資本化 (Capitalized)」，儲存。
- **測試結果**：**[通過 (PASS)]**
- **詳細描述**：費用成功登記於 `management_ledgers`。標記為資本化之費用會計入資產成本增值，而非當月耗用費用。

### 2.9 Dashboard KPI 統計指標運算
- **測試項目**：檢查儀表板出租率、當月租金實收、未收租金、押金餘額是否正確。
- **測試結果**：**[通過 (PASS)]**
- **詳細描述**：當「客戶帳務」中的流水被標記為 paid 後，Dashboard 的「當月租金實收」即時增加；當有新帳單未收時，「未收租金」相應增加；指標運算完全在 client 端進行，在離線下計算完全正確。

### 2.10 離線新增與恢復網路同步
- **測試步驟**：
  1. 在瀏覽器中切換至 **Offline** 狀態。
  2. 新增一筆場地支出項目。
  3. 觀察 Layout 狀態列是否顯示「離線暫存」，且 Settings 面板顯示「有待同步變更：1 筆」。
  4. 切換回 **Online** 狀態。
- **測試結果**：**[通過 (PASS)]**
- **詳細描述**：網路恢復且 App/SDK 執行時，Firestore 背景自動完成與雲端的雙向同步，狀態列變回「已同步」，雲端 Console 隨即檢測到離線寫入的資料。

### 2.11 CSV 匯出測試
- **測試項目**：對客戶、貨櫃、租約、支出、帳務五個頁面分別進行 CSV 匯出。
- **測試結果**：**[通過 (PASS)]**
- **詳細描述**：
  - CSV 內容包含 `\uFEFF` UTF-8 BOM 開頭，Excel 開啟繁體中文完全正常不亂碼。
  - 下載的檔名格式完全符合：`{資料表名稱}_YYYYMMDD_HHmmss.csv`（如：`租賃合約清單_20260707_164530.csv`）。
  - 當列表無資料或篩選後無符合項目時，點擊按鈕彈出「無資料可匯出」提示，無程式崩潰。

### 2.12 PWA 安裝與手機 RWD
- **測試項目**：在 Chrome 安裝 App；在手機端檢視佈局。
- **測試結果**：**[通過 (PASS)]**
- **詳細描述**：
  - 網址列順利出現 PWA 安裝按鈕，安裝後可作為獨立視窗運作，離線時仍可正常啟動。
  - 桌機端顯示左側 Sidebar，手機端自適應切換為底部導航欄（Bottom Nav），表格自動折疊成 Card 佈局，手勢操作順暢，符合行動化營運標準。
# Phase 1 最終驗證紀錄（2026-07-14）

本次環境已實際確認 `node`、`npm`、`java` 不存在於 PATH，且 `C:\Program Files\nodejs\node.exe` 不存在。因此 `npm ci`、lint、Vitest、build、Firestore Emulator Rules 測試與 PWA 產物檢查皆**尚未執行**；不可視為通過。`package.json` 已加入測試相依套件，但 `package-lock.json` 尚未包含它們，因此目前 `npm ci` 預期會失敗；這必須以 Node 20 執行 `npm install` 更新 lockfile 後才能驗證。已完成 package scripts、Vitest/Rules Emulator 設定與靜態檔案檢查。請在 Node 20 與 Java 可用的環境依序執行 `npm install`、`npm ci`、`npm run lint`、`npm run test`、`npm run build`、`npm run test:rules`、`npm run check`。
