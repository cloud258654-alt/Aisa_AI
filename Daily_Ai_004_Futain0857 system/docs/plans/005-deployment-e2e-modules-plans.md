---
plan_id: "005"
title: "正式部署、PWA 與端到端驗證"
status: "verification-pending"
depends_on: ["001", "002", "003", "004"]
format_version: 1
last_updated: "2026-07-21"
---

# 005 — 正式部署、PWA 與端到端驗證

## 目標

完成正式 Google Sheets、GAS Web App、React 前端及 PWA 的部署與端到端驗證。

## 環境

至少建立：

```text
TEST
PRODUCTION
```

測試與正式環境不得共用 Spreadsheet。

## GAS 部署

1. 建立測試及正式試算表。
2. 執行新版 `setupSpreadsheet()`。
3. 設定 Script Properties：

```text
SPREADSHEET_ID
ADMIN_USERNAME
PASSWORD_SALT
PASSWORD_HASH
SESSION_SECRET
SESSION_TTL_SECONDS
```

4. `.clasp` 綁定真實 Script ID。
5. 部署 GAS Web App。
6. 驗證：
   - health
   - login
   - session
   - list/get
   - 核心寫入流程
7. 記錄 Deployment ID、版本及部署日期。

不得將 Secret 或正式 Spreadsheet ID 提交 Git。

## 前端部署

環境變數：

```env
VITE_GAS_WEB_APP_URL=https://script.google.com/macros/s/DEPLOYMENT_ID/exec
```

檢查：

```bash
cd "Daily_Ai_004_Futain0857 system/container-rental-app-v1"
npm ci
npm run lint
npm run test
npm run build
```

## PWA

驗證：

- Manifest 名稱、圖示與主題色。
- HTTPS。
- 可安裝。
- 新版本更新提示。
- 靜態資源快取。
- 業務資料離線時不允許誤以為已儲存。
- 離線提交按鈕顯示明確提示。

MVP 只支援靜態 PWA 快取，不實作複雜離線資料同步。

## 端到端流程

```text
登入
→ 建立客戶
→ 建立貨櫃
→ 建立費率
→ 建立多櫃合約
→ 產生押金及分期應收
→ 部分付款
→ 完成付款
→ 續約
→ 退租扣款
→ 押金退款
→ 貨櫃檢查
→ 恢復可出租
→ 新增支出
→ 匯出報表
→ 查看稽核
```

## 裝置與瀏覽器

最低驗證：

- Windows Chrome
- Windows Edge
- Android Chrome
- iPhone Safari
- 390px 手機
- 768px 平板
- 1440px 桌機

## CSV

- UTF-8 BOM。
- 中文欄名。
- 日期及金額格式可讀。
- Excel 開啟不亂碼。
- 押金、租金、付款及支出分開匯出。

## 備份與復原

新增：

```text
project_management/BACKUP_RESTORE.md
```

內容：

- 備份頻率。
- 試算表複製。
- Script Properties 管理。
- 測試環境還原。
- 遷移失敗回復。
- 負責人及位置。
- 一次實際復原演練紀錄。

## 驗收條件

- [ ] 測試及正式環境隔離。
- [ ] 正式 GAS 部署成功。
- [ ] 正式前端可登入。
- [ ] 完整端到端流程通過。
- [ ] Windows、Android、iPhone 基本流程通過。
- [ ] PWA 安裝與離線提示正確。
- [ ] CSV 中文正常。
- [ ] 備份及還原演練成功。
- [ ] CI、lint、test、build 通過。
- [ ] `DEPLOYMENT.md`、`TEST_REPORT.md` 已更新。

## Antigravity IDE 執行指令

```text
先在 TEST 環境完成全部端到端測試。
不得直接用正式資料測試遷移或退租。
只有 TEST 驗收全部通過後，才產生 PRODUCTION 部署清單。
不得把 Secret 寫入 Markdown、程式碼或 Git。
```
