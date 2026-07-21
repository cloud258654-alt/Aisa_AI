---
plan_id: "000"
title: "貨櫃出租系統 MVP 模組計畫索引"
status: "planned"
document_type: "plan-index"
format_version: 1
last_updated: "2026-07-21"
---

# 貨櫃出租系統 MVP 模組計畫索引

## 目的

本目錄將福田貨櫃倉儲出租系統的剩餘工作拆成可由 Antigravity IDE 逐階段執行、測試與驗收的 Markdown 計畫。

## 專案路徑

```text
Daily_Ai_004_Futain0857 system/
├── apps-script/
├── container-rental-app-v1/
└── docs/
    └── plans/
        ├── 000-index-modules-plans.md
        ├── 001-data-model-modules-plans.md
        ├── 002-core-workflows-modules-plans.md
        ├── 003-consistency-security-modules-plans.md
        ├── 004-ui-ux-modules-plans.md
        ├── 005-deployment-e2e-modules-plans.md
        ├── 006-customer-acceptance-modules-plans.md
        └── 007-markdown-docs-center-modules-plans.md
```

## 執行順序

| 順序 | 文件 | 主要終點 |
|---:|---|---|
| 1 | `001-data-model-modules-plans.md` | 多櫃合約、費率、應收與收款資料模型定版 |
| 2 | `002-core-workflows-modules-plans.md` | 建約、收款、續約、退租四條流程完成 |
| 3 | `003-consistency-security-modules-plans.md` | 防重複、狀態機、Session 與稽核完成 |
| 4 | `004-ui-ux-modules-plans.md` | 深藍金色 RWD UI 與操作流程完成 |
| 5 | `005-deployment-e2e-modules-plans.md` | 正式 GAS、前端、PWA 與端到端測試完成 |
| 6 | `006-customer-acceptance-modules-plans.md` | 客戶驗收、手冊、交接與 v1.0.0 完成 |
| 7 | `007-markdown-docs-center-modules-plans.md` | Markdown 文件中心、預覽與 WYSIWYG 介面完成 |

## Antigravity IDE 共通規則

1. 一次只執行一份計畫，不得同時跨階段大改。
2. 先讀取實際程式碼，再依計畫建立差異分析。
3. 每次修改後執行：

```bash
cd "Daily_Ai_004_Futain0857 system/container-rental-app-v1"
npm run lint
npm run test
npm run build
```

4. GAS 變更必須同步更新 `ManualTests.gs`。
5. 每階段更新：
   - `project_management/CHANGELOG.md`
   - `project_management/API_SPEC.md`
   - `project_management/DATABASE_SCHEMA.md`
   - `project_management/TEST_REPORT.md`
6. 完成後停止並回報，等待人工核准才進入下一份計畫。
7. 不得重新引入 Firebase、Firestore、Supabase 或獨立 HTTP Backend。
8. 不得在 Git 中提交 Script Properties、密碼、Token 或正式 Spreadsheet ID。

## 每階段回報格式

```markdown
## 執行結果

### 完成項目
- ...

### 修改檔案
- `path/to/file`

### Schema／API 變更
- ...

### 測試結果
- Lint：PASS／FAIL
- Unit tests：PASS／FAIL
- Build：PASS／FAIL
- GAS Manual Tests：PASS／FAIL

### 未解決問題
- ...

### 人工驗收步驟
1. ...

### 下一階段前置條件
- ...
```

## MVP 最終 Definition of Done

- [ ] 一份合約可包含多個貨櫃。
- [ ] 同一期間不可重複出租同一貨櫃。
- [ ] 費率、分期、應收、收款、押金及退款可追蹤。
- [ ] 續約不覆寫舊合約。
- [ ] 退租後貨櫃先檢查再重新出租。
- [ ] 重複請求不產生重複資料。
- [ ] Dashboard 與原始資料一致。
- [ ] 所有關鍵操作可稽核。
- [ ] 桌機、平板、手機可操作。
- [ ] 正式部署、備份、還原與客戶驗收完成。
- [ ] 發布 `v1.0.0`。
