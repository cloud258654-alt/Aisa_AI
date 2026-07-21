import { useState } from 'react';
import PageHeader from '../components/ui/PageHeader';
import TerminationWizard from '../components/contracts/TerminationWizard';
import { TerminationIcon } from '../components/ui/Icons';

export default function TerminationPage() {
  const [isWizardOpen, setIsWizardOpen] = useState(true);

  return (
    <div className="space-y-6">
      <PageHeader
        title="退租結算與貨櫃檢查管理"
        description="辦理合約退租啟動、7 步驟押金與遙控器扣款試算，以及現場檢查通過後將貨櫃解鎖為 AVAILABLE。"
        actionButton={
          !isWizardOpen ? (
            <button
              onClick={() => setIsWizardOpen(true)}
              className="px-4 py-2 bg-brand-navy-950 hover:bg-brand-navy-900 text-white rounded-lg text-xs font-semibold shadow-sm flex items-center gap-2"
            >
              <TerminationIcon className="w-4 h-4 text-brand-gold-300" /> 辦理新退租結算 (Wizard)
            </button>
          ) : undefined
        }
      />

      {isWizardOpen ? (
        <TerminationWizard
          onSuccess={() => setIsWizardOpen(false)}
          onCancel={() => setIsWizardOpen(false)}
        />
      ) : (
        <div className="saas-card p-12 text-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-surface-muted mx-auto flex items-center justify-center text-brand-navy-950 border border-border-default shadow-xs">
            <TerminationIcon className="w-8 h-8 text-brand-navy-950" />
          </div>
          <h3 className="text-lg font-bold text-brand-navy-950">退租結算與貨櫃檢驗 Wizard</h3>
          <p className="text-xs sm:text-sm text-text-secondary max-w-md mx-auto">
            點選下方按鈕開啟 7 步驟退租 Wizard，引導完成合約結算、遙控器盤點與貨櫃驗收解鎖。
          </p>
          <button
            onClick={() => setIsWizardOpen(true)}
            className="px-6 py-2.5 bg-brand-navy-950 text-white font-semibold text-xs rounded-lg shadow-sm"
          >
            開啟退租結算 Wizard ➔
          </button>
        </div>
      )}
    </div>
  );
}
