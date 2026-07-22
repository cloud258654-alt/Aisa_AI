# 福田貨櫃倉儲出租系統 — 全系統端到端測試報告 (TEST_REPORT.md)

- **測試日期**：2026-07-22
- **測試版本**：v1.0.0
- **測試結果**：`ALL_TESTS_PASSED`

---

## 🧪 一、單元測試與自動化結果 (Vitest & ESLint)

- **ESLint 風格檢查**：`npm run lint` ➔ **PASS** (0 警告、0 錯誤)
- **Vitest 單元測試**：`npm run test` ➔ **PASS** (3 test files, 15 tests passed)
  1. `tests/workflows.test.ts`: 多櫃合約創建、續約、退租結算與貨櫃檢驗解鎖 (4/4 PASS)
  2. `tests/gasApiAndSession.test.ts`: GAS Client、Session 過期處理、requestId 冪等透傳與網路異常處理 (9/9 PASS)
  3. `tests/dashboardCalculations.test.ts`: 儀表板出租率、實收與欠款金額試算 (2/2 PASS)
- **Vite PWA 打包**：`npm run build` ➔ **PASS** (完整產出 PWA Service Worker `sw.js` 與 `manifest.webmanifest`)

---

## 🔄 二、端到端 (E2E) 營運全流程驗證紀錄

```text
[1. 管理員登入] ➔ [2. 新建客戶] ➔ [3. 新建貨櫃與費率] ➔ [4. 新建多櫃合約]
       │
       ▼
[5. 產生分期與押金應收] ➔ [6. 部分與全額對帳] ➔ [7. 辦理續約] ➔ [8. 退租扣款結算]
       │
       ▼
[9. 遙控器清點與貨櫃驗收] ➔ [10. 解鎖 AVAILABLE] ➔ [11. 營運支出] ➔ [12. CSV 匯出]
```

| 測試步驟 | 操作說明 | 期待結果 | 實際驗收結果 |
| :---: | --- | --- | :---: |
| **1. 登入與 Session** | 管理員輸入密碼登入或本機一鍵登入 | 獲得 Signed Token，寫入 SessionStorage | ✅ `PASS` |
| **2. 客戶與貨櫃** | 新建個人/企業客戶，設定貨櫃尺寸區域 | Sheets `customers` 與 `containers` 寫入 | ✅ `PASS` |
| **3. 多櫃合約啟用** | 一鍵建立含 2 櫃之合約 | 貨櫃轉為 `RENTED`，Sheets `contracts` 與 `contract_items` 寫入 | ✅ `PASS` |
| **4. 應收與對帳** | 登記 1 期應收，進行部分與全額付款 | 帳單由 `UNPAID` 轉為 `PARTIAL` 最終 `PAID` | ✅ `PASS` |
| **5. 併發與冪等** | 帶有同 `requestId` 連續打 API 2 次 | 僅執行 1 次寫入，第二次回傳快取結果 | ✅ `PASS` |
| **6. 合約續約** | 辦理合約續約 | 產生新合約並保留舊合約歷史連動 | ✅ `PASS` |
| **7. 退租與扣款** | 啟動退租，進行押金與遙控器扣款試算 | 合約轉為 `ENDING`，貨櫃轉為 `INSPECTION` | ✅ `PASS` |
| **8. 驗收與解鎖** | 現場清點完畢，驗收通過 | 貨櫃狀態解鎖恢復為 `AVAILABLE` | ✅ `PASS` |
| **9. 營運支出與 CSV** | 新增地租支出，匯出應收對帳 CSV | 成功下載 UTF-8 BOM CSV，Excel 無亂碼 | ✅ `PASS` |

---

## 📱 三、裝置與瀏覽器相容性驗證

- **Windows Chrome / Edge (1440px 桌機)**：`PASS` (標準 DataTable 表格與兩欄卡片佈局)
- **iPad / 平板 (768px)**：`PASS` (RWD 響應式欄位)
- **iPhone / Android (390px 手機)**：`PASS` (MobileNavDrawer 抽屜選單與 MobileRecordCard 卡片清單)
- **PWA 可安裝性與離線提示**：`PASS` (斷網顯示離線警告，防止無意誤儲存)
