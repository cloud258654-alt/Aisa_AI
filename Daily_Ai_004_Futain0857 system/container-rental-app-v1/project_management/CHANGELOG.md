# 貨櫃出租 App V1 - 專案異動紀錄 (Changelog) - Firebase Firestore 版

本檔案記錄本專案 V1.0.0 各階段的開發里程碑與重大架構變更。

---

## [1.0.0] - 2026-07-07

### Added (新增)

- **前端專案初始化**
  - 使用 Vite 建立 React + TypeScript 專案。
  - 安裝必要相依套件：`react-router-dom`、`firebase`、`dexie`（預留）、`date-fns`、`zod` 以及 `vite-plugin-pwa`。
  - 導入 Tailwind CSS v3 並完成 `tailwind.config.js` 配置。
  - 設定 `src/index.css`，加入 Google Font (Outfit)、滾動條美化、玻璃磨砂效果（Glassmorphic Panels/Inputs）及進出場微動畫。

- **資料結構與型別定義**
  - 建立對應資料儲存的五大核心型別結構：
    - `src/types/customer.ts` (客戶資料)
    - `src/types/container.ts` (貨櫃主檔)
    - `src/types/rentalRecord.ts` (租約紀錄)
    - `src/types/customerLedger.ts` (對客收付款流水)
    - `src/types/managementLedger.ts` (場地營運支出)

- **Firebase Firestore 雲端同步與離線快取**
  - 實作 `src/services/firebase/firebase.ts` 初始化 Firebase 應用與 Firestore 實例。
  - 啟用 Firestore 離線持久化快取 (IndexedDB Local Persistence) 以及多網頁分頁狀態管理器，允許離線狀態下資料寫入本地快取並即時渲染 UI。
  - 當網路恢復且 **App/SDK 處於執行狀態下時**，系統會自動在背景默默將變更同步上傳至雲端。

- **交易與原子性寫入控制 (Transaction & Atomic Writes)**
  - 在新建租約與退約時，使用 `runTransaction` 進行嚴格的資料校驗，包含先讀取檢核貨櫃狀態是否為 `available`，且目前無其他生效中的租賃合約，檢查無誤後再原子性地寫入合約、更新狀態與發送首期帳務明細，防範並發衝突。

- **RWD 版型與頁面 UI 開發**
  - 實作 Layout 框架：PC 側邊選單欄 + 手機端底部導航條，配合狀態列即時顯示 Online/Offline 狀態、來自 Cache 或雲端之標記、是否有 pending writes 待同步項目以及最近更新時間。
  - **DashboardPage**：整合 10 大統計核心指標，包含出租率進度條、財務收支欠款統計，並列出 30 天內即將到期合約，純前端即時聚合計算，離線亦可使用。
  - **CustomersPage**：客戶列表與詳細帳務彈窗，右上角支援 CSV 匯出。
  - **ContainersPage**：支援電腦版 Table 與手機版 Card 的回應式排版，右上角支援 CSV 匯出。
  - **RentalsPage**：實作 3 步驟租賃簽約精靈（選客戶 ➔ 選空櫃 ➔ 合約條款設定），支援自動產生首月租金/押金流水，右上角支援 CSV 匯出。
  - **CustomerLedgersPage**：管理帳單明細、收退押金與租金應收，支援單筆登記收款與 CSV 格式匯出。
  - **ManagementLedgersPage**：登記各項營運公攤水電與特定貨櫃修繕，支援資本化 (Capitalized Expense) 切換，右上角支援 CSV 匯出。
  - **SettingsPage**：提供 Firebase 憑證手動設定（儲存於 localStorage，供 Demo 開發調試使用）、Firestore 集合說明，以及即時同步中繼資料（Metadata）狀態面板。

- **PWA 整合**
  - 繪製專屬 `container.svg` 向量應用程式圖標。
  - 於 `vite.config.ts` 與 `index.html` 整合 `vite-plugin-pwa` 配置，產生 Service Worker 與離線 Precaching，支援將 App 安裝至手機主畫面。

- **打包相容性處理**
  - 撰寫 `preload-crypto.cjs` 腳本，完美解決 Node.js 18 環境下 Rollup Terser Plugin 缺乏 global.crypto 導致的打包編譯錯誤。
# Changelog

## [1.1.0] - 2026-07-14
- 導入 users Profile、角色權限與拒絕缺失/停用 Profile 的登入流程。
- 重寫 Firestore Rules、移除瀏覽器動態 Firebase 設定，新增測試、CI 與部署文件。
- 最終驗證修正：CI workflow 移至儲存庫根目錄，補上頁面角色按鈕限制與 staff 貨櫃欄位限制；Node/npm/Java 缺失使實際驗證待後續環境執行。
