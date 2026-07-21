---
release: "v1.0.0-rc1"
development: "complete"
documentation: "complete"
test-deployment: "verification-pending"
production: "blocked"
customer-uat: "prepared"
customer-uat-result: "pending"
---

# Phase 006-A-2 — Release Candidate 收尾補正 (已完成工作與交接紀錄)

- **完成日期**：2026-07-22
- **執行階段**：Phase 006-A-2 (`006-customer-acceptance-modules-plans.md`)
- **發行版本**：`v1.0.0-rc1` (Release Candidate)
- **當前門禁**：`PRODUCTION_BLOCKED` / `TEST_VERIFICATION_PENDING`

---

## 📋 1. RC1 收尾工作完成核對表

| 收尾驗收項目 | 修正與落實內容 | 驗收結果 |
| :---: | --- | :---: |
| **Release Notes 修正** | 重建 `docs/release/release-notes-v1.0.0-rc1.md`，明確標示 `v1.0.0-rc1` 與 `Production: Not Yet Approved`。 | ✅ `PASS` |
| **交接與門禁清單** | 建立 `handover-checklist.md` 與標記 `Production Status: BLOCKED` 之 `production-gate-checklist.md`。 | ✅ `PASS` |
| **品牌名稱盤點** | 建立 `branding-name-decision.md` 標示 `PENDING USER DECISION`，記錄 23 處出現位置，無擅自全域取代。 | ✅ `PASS` |
| **30 項 UAT 矩陣** | 擴充 `customer-acceptance-test.md` 至 30 項案例，全數未實測驗證項目統一標示為 `PENDING`。 | ✅ `PASS` |
| **快捷登入安全修正** | `LoginPage.tsx` 加上 `!import.meta.env.PROD`，限制一鍵登入僅在 DEV/TEST 顯示，正式 Production 打包自動隱藏。 | ✅ `PASS` |
| **未解決問題書面揭露** | 誠實列出 TEST Gate 未人工實測、Production 未核准、UAT 待簽核、品牌名稱待定等 7 大問題。 | ✅ `PASS` |

---

## 📁 2. 異動與新增檔案清單

- `docs/release/release-notes-v1.0.0-rc1.md` (新增，RC1 發行說明)
- `docs/acceptance/handover-checklist.md` (新增，交接檢核表)
- `docs/acceptance/production-gate-checklist.md` (新增，Production 生產門禁審查清單)
- `docs/acceptance/branding-name-decision.md` (新增，品牌名稱盤點與決策表)
- `docs/acceptance/customer-acceptance-test.md` (修改，擴充為 30 項 `PENDING` 驗收矩陣)
- `container-rental-app-v1/src/pages/LoginPage.tsx` (修改，生產模式隱藏快捷登入按鈕)
- `docs/user/quick-start.md` & `user-operation-manual.md` (修改，標記快捷登入為 TEST ONLY)
- `docs/Finished/006-a-pre-release-closeout-finished.md` (本報告)
- `docs/Finished/WORK_HANDOVER_LOG.md` (更新)

---

## 🧪 3. 自動化測試驗證

1. **ESLint 靜態檢查**：`npm run lint` ➔ **PASS** (0 警告、0 錯誤)
2. **Vitest 單元測試**：`npm run test` ➔ **PASS** (3 test files, 15 tests passed)
3. **Vite Production Build**：`npm run build` ➔ **PASS** (建置成功，生產模式不渲染快捷登入按鈕)

---

## ⚠️ 4. 誠實列出未解決問題 (Unresolved Issues)

1. **TEST Gate 尚未完成人工實際網頁與 Sheets 跨介面驗證**
2. **Production 正式部署未獲得使用者核准 (BLOCKED)**
3. **客戶 30 項 UAT 驗收測試尚未完成實際操作簽核 (標記為 PENDING)**
4. **行動端 (Android / iPhone) 實體裝置驗證待完成**
5. **品牌統一名稱待使用者決定 (`branding-name-decision.md` 為 PENDING USER DECISION)**
6. **Google Sheets 非交易型 ACID 與 Apps Script 執行流量限制**
7. **單一管理員模式限制 (未支援 RBAC 多角色權限分級)**
