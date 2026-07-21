import { useState } from 'react';
import { createAndActivateContract } from '../../services/api/contractsApi';
import StatusBadge from '../ui/StatusBadge';
import { ContractsIcon } from '../ui/Icons';

interface ContractWizardProps {
  onSuccess: () => void;
  onCancel: () => void;
}

export default function ContractWizard({ onSuccess, onCancel }: ContractWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [customerId, setCustomerId] = useState('CUST-001');
  const [containerId1, setContainerId1] = useState('CONT-001');
  const [containerId2, setContainerId2] = useState('');
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0]);
  const [rentTotal, setRentTotal] = useState('48000');
  const [depositTotal, setDepositTotal] = useState('5000');
  const [installmentCount, setInstallmentCount] = useState('2');

  const steps = [
    { num: 1, title: '選擇客戶' },
    { num: 2, title: '選擇貨櫃' },
    { num: 3, title: '費率租期' },
    { num: 4, title: '押金分期' },
    { num: 5, title: '合約預覽' },
    { num: 6, title: '啟用完成' }
  ];

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const items = [
        {
          container_id: containerId1,
          unit_price: Number(rentTotal),
          discount_amount: 0,
          effective_price: Number(rentTotal),
          start_date: startDate,
          status: 'ACTIVE' as const
        }
      ];
      if (containerId2) {
        items.push({
          container_id: containerId2,
          unit_price: Number(rentTotal),
          discount_amount: 0,
          effective_price: Number(rentTotal),
          start_date: startDate,
          status: 'ACTIVE' as const
        });
      }

      await createAndActivateContract({
        requestId: 'REQ-WIZARD-' + Date.now(),
        customer_id: customerId,
        start_date: startDate,
        rent_total: Number(rentTotal),
        deposit_total: Number(depositTotal),
        installment_count: Number(installmentCount),
        items
      });

      setCurrentStep(6);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : '啟用合約失敗');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="saas-card p-6 space-y-6">
      {/* Wizard Progress Bar */}
      <div className="border-b border-border-default pb-4">
        <div className="flex items-center justify-between overflow-x-auto gap-2">
          {steps.map((s) => (
            <div key={s.num} className="flex items-center gap-2 shrink-0">
              <div
                className={`w-7 h-7 rounded-full text-xs font-bold flex items-center justify-center transition-all ${
                  currentStep === s.num
                    ? 'bg-brand-navy-950 text-white ring-2 ring-brand-gold-500'
                    : currentStep > s.num
                    ? 'bg-status-success text-white'
                    : 'bg-surface-muted text-text-secondary border border-border-default'
                }`}
              >
                {currentStep > s.num ? '✓' : s.num}
              </div>
              <span
                className={`text-xs font-medium ${
                  currentStep === s.num ? 'text-brand-navy-950 font-bold' : 'text-text-secondary'
                }`}
              >
                {s.title}
              </span>
              {s.num < steps.length && <span className="text-text-secondary text-xs">➔</span>}
            </div>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 text-status-danger text-xs rounded-lg">
          ⚠️ {error}
        </div>
      )}

      {/* Step Contents */}
      <div className="min-h-[220px]">
        <div className="flex items-center gap-2 mb-6">
          <ContractsIcon className="w-5 h-5 text-brand-gold-500" />
          <h3 className="font-bold text-lg text-brand-navy-950">新建合約引導精靈 (6 步驟)</h3>
        </div>
        {currentStep === 1 && (
          <div className="space-y-4">
            <h3 className="font-bold text-base text-brand-navy-950">Step 1: 選擇承租客戶</h3>
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1">客戶 ID</label>
              <input
                type="text"
                value={customerId}
                onChange={(e) => setCustomerId(e.target.value)}
                placeholder="例如 CUST-001"
                className="w-full saas-input max-w-md"
              />
              <p className="text-[11px] text-text-secondary mt-1">必須為狀態啟用 (ACTIVE) 之有效客戶</p>
            </div>
          </div>
        )}

        {currentStep === 2 && (
          <div className="space-y-4">
            <h3 className="font-bold text-base text-brand-navy-950">Step 2: 選擇承租貨櫃 (可單櫃或多櫃)</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-lg">
              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1">主貨櫃 ID (必填)</label>
                <input
                  type="text"
                  value={containerId1}
                  onChange={(e) => setContainerId1(e.target.value)}
                  placeholder="例如 CONT-001"
                  className="w-full saas-input"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1">附屬貨櫃 ID (選填多櫃)</label>
                <input
                  type="text"
                  value={containerId2}
                  onChange={(e) => setContainerId2(e.target.value)}
                  placeholder="例如 CONT-002"
                  className="w-full saas-input"
                />
              </div>
            </div>
          </div>
        )}

        {currentStep === 3 && (
          <div className="space-y-4">
            <h3 className="font-bold text-base text-brand-navy-950">Step 3: 設定起租日期與年總租金</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-lg">
              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1">起租日期</label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full saas-input"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1">租金總額 (元)</label>
                <input
                  type="number"
                  value={rentTotal}
                  onChange={(e) => setRentTotal(e.target.value)}
                  className="w-full saas-input"
                />
              </div>
            </div>
          </div>
        )}

        {currentStep === 4 && (
          <div className="space-y-4">
            <h3 className="font-bold text-base text-brand-navy-950">Step 4: 押金與分期數</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-lg">
              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1">押金金額 (元)</label>
                <input
                  type="number"
                  value={depositTotal}
                  onChange={(e) => setDepositTotal(e.target.value)}
                  className="w-full saas-input"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1">分期期數 (期)</label>
                <input
                  type="number"
                  value={installmentCount}
                  onChange={(e) => setInstallmentCount(e.target.value)}
                  className="w-full saas-input"
                />
              </div>
            </div>
          </div>
        )}

        {currentStep === 5 && (
          <div className="space-y-4 bg-surface-muted p-4 rounded-lg border border-border-default">
            <h3 className="font-bold text-base text-brand-navy-950">Step 5: 合約條款預覽</h3>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div><span className="text-text-secondary">客戶 ID：</span><span className="font-bold">{customerId}</span></div>
              <div><span className="text-text-secondary">起租日期：</span><span className="font-bold">{startDate}</span></div>
              <div><span className="text-text-secondary">承租貨櫃：</span><span className="font-bold">{containerId1} {containerId2 ? `, ${containerId2}` : ''}</span></div>
              <div><span className="text-text-secondary">租金總額：</span><span className="font-bold text-brand-navy-950">${Number(rentTotal).toLocaleString()}</span></div>
              <div><span className="text-text-secondary">押金總額：</span><span className="font-bold text-amber-700">${Number(depositTotal).toLocaleString()}</span></div>
              <div><span className="text-text-secondary">每期租金：</span><span className="font-bold">${Math.floor(Number(rentTotal) / Number(installmentCount)).toLocaleString()} / 期 (共 {installmentCount} 期)</span></div>
            </div>
          </div>
        )}

        {currentStep === 6 && (
          <div className="text-center space-y-3 py-6">
            <div className="w-12 h-12 bg-emerald-100 text-status-success rounded-full flex items-center justify-center text-2xl mx-auto">
              ✓
            </div>
            <h3 className="font-bold text-lg text-brand-navy-950">合約建立與啟用成功！</h3>
            <p className="text-xs text-text-secondary">後端已單一交易完成貨櫃狀態變更為 RENTED 並自動開立押金與分期租金帳單。</p>
            <StatusBadge status="ACTIVE" />
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-4 border-t border-border-default">
        {currentStep < 6 ? (
          <>
            <button
              onClick={currentStep === 1 ? onCancel : () => setCurrentStep((prev) => prev - 1)}
              className="px-4 py-2 text-xs font-semibold text-text-secondary hover:bg-surface-muted rounded-lg border border-border-default"
            >
              {currentStep === 1 ? '取消' : '上一步'}
            </button>

            {currentStep < 5 ? (
              <button
                onClick={() => setCurrentStep((prev) => prev + 1)}
                className="px-4 py-2 bg-brand-navy-950 hover:bg-brand-navy-900 text-white rounded-lg text-xs font-semibold"
              >
                下一步 ➔
              </button>
            ) : (
              <button
                onClick={() => void handleSubmit()}
                disabled={loading}
                className="px-6 py-2 bg-gradient-to-r from-brand-navy-950 to-brand-navy-900 text-white rounded-lg text-xs font-semibold shadow-md disabled:opacity-50"
              >
                {loading ? '啟用中...' : '確認啟用合約'}
              </button>
            )}
          </>
        ) : (
          <button
            onClick={onSuccess}
            className="w-full py-2.5 bg-brand-navy-950 text-white rounded-lg text-xs font-semibold"
          >
            完成並返回合約列表
          </button>
        )}
      </div>
    </div>
  );
}
