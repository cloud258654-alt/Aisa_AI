import PageHeader from '../components/ui/PageHeader';
import StatusBadge from '../components/ui/StatusBadge';

export default function SettingsPage() {
  const gasUrl = import.meta.env.VITE_GAS_WEB_APP_URL || '未設定 (請於 .env.local 配置)';

  return (
    <div className="space-y-6">
      <PageHeader
        title="系統設定與環境配置"
        description="檢視 Google Apps Script 後端部署網址、Session 會期設定與單一管理員模式宣告。"
      />

      <div className="saas-card p-6 space-y-6">
        <div>
          <h3 className="font-bold text-base text-brand-navy-950 border-b border-border-default pb-2 mb-3">
            🌐 廣域 API 與後端連線
          </h3>
          <div className="space-y-2 text-xs">
            <div>
              <span className="text-text-secondary font-medium block mb-1">GAS Web App 連線 URL:</span>
              <code className="p-2.5 bg-surface-muted rounded-lg border border-border-default font-mono text-brand-navy-950 block overflow-x-auto">
                {gasUrl}
              </code>
            </div>
            <p className="text-text-secondary">
              資料同步庫存：Google Sheets 8 大核心資料表 (`containers`, `contracts`, `invoices`, `payments` 等)
            </p>
          </div>
        </div>

        <div>
          <h3 className="font-bold text-base text-brand-navy-950 border-b border-border-default pb-2 mb-3">
            🔐 Session 安全與會期設定
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="p-3.5 bg-surface-muted rounded-lg border border-border-default space-y-1">
              <span className="text-text-secondary">會期憑證類型：</span>
              <span className="font-bold text-brand-navy-950 block">HMAC-SHA256 Signed Token</span>
            </div>
            <div className="p-3.5 bg-surface-muted rounded-lg border border-border-default space-y-1">
              <span className="text-text-secondary">預設有效時間：</span>
              <span className="font-bold text-brand-navy-950 block">86,400 秒 (24 小時)</span>
            </div>
          </div>
        </div>

        <div>
          <h3 className="font-bold text-base text-brand-navy-950 border-b border-border-default pb-2 mb-3">
            ⚠️ 系統模式與權限矩陣
          </h3>
          <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg text-xs space-y-2 text-amber-800">
            <div className="flex items-center gap-2">
              <StatusBadge status="ACTIVE" customLabel="單一管理員模式 (Single Admin)" />
            </div>
            <p className="leading-relaxed">
              本系統目前採取單一管理員權限控制，全域實施排他鎖與 <code>requestId</code> 寫入冪等保護。**目前尚未支援多角色權限與 RBAC (Role-Based Access Control) 存取控制矩陣**。
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
