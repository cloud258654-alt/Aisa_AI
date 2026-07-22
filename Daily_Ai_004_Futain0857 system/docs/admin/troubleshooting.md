# 福田貨櫃倉儲出租系統 — 疑難排解與常見問題處置 (Troubleshooting)

- **版本**：v1.0.0

---

## 1. 常見部署與連線問題

### 1.1 呼叫 GAS Web App 傳回 302 或 CORS 阻擋
- **原因**：Web App 部署權限設定錯誤。
- **解決方案**：開啟 GAS 部署設定，確認「誰可以存取 (Who has access)」設定為 **「所有人 (Anyone)」**。

### 1.2 前端顯示「登入已逾期」
- **原因**：HMAC Session Token 已超過 24 小時。
- **解決方案**：重新輸入管理員密碼登入。

### 1.3 貨櫃狀態無法由 RENTED 改為 AVAILABLE
- **原因**：後端 `StateMachine.gs` 預檢白名單保護，禁止直接改狀態。
- **解決方案**：必須透過 `TerminationWizard` 完成退租與驗收解鎖。
