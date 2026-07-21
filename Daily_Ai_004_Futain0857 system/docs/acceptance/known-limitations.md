# 富田貨櫃出租系統 — 已知限制與邊界聲明 (Known Limitations)

- **版本**：v1.0.0

---

## ⚠️ 系統限制書面揭露事項

1. **試算表非 ACID 資料庫**：
   - Google Sheets 不具備原生 ACID 資料庫 Transaction 與自動 Rollback 功能。系統已實施 `LockService` 與 `requestId` 冪等防護，但仍需保留定期備份。

2. **GAS 執行與配額限制**：
   - Google Apps Script 每次 HTTP 執行超時限制為 6 分鐘，每日觸發器執行有配額限制。

3. **單一管理員模型 (Single Admin)**：
   - 目前採單一管理員身份認證，尚未擴充 Role-Based Access Control (RBAC) 多角色細粒度權限控制。

4. **PWA 靜態快取與離線邊界**：
   - MVP 版本 PWA 支援靜態資源快取與斷網防誤儲存提示，不包含離線資料寫入並行同步。

5. **未整合外部第三方服務**：
   - 尚未整合第三方線上金流 (如綠界/藍新)、電子簽章、LINE Notify API 或智慧門禁。

6. **人工備份處置**：
   - 營運單位需依 [BACKUP_RESTORE.md](file:///e:/Ai%20study/Aisa_AI/Daily_Ai_004_Futain0857%20system/project_management/BACKUP_RESTORE.md) 維持每日備份作業。
