import { useState } from 'react';
import { startTermination, completeTermination, completeContainerInspection } from '../../services/api/terminationsApi';
import StatusBadge from '../ui/StatusBadge';

interface TerminationWizardProps {
  onSuccess: () => void;
  onCancel: () => void;
}

export default function TerminationWizard({ onSuccess, onCancel }: TerminationWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [contractId, setContractId] = useState('CNT-CASE-A');
  const [containerId, setContainerId] = useState('CONT-CASE-A');
  const [remoteExpected, setRemoteExpected] = useState('1');
  const [remoteReturned, setRemoteReturned] = useState('0');
  const [cleaningFee, setCleaningFee] = useState('1000');
  const [damageFee, setDamageFee] = useState('0');
  const [depositOriginal, setDepositOriginal] = useState('10000');

  const [refundSummary, setRefundSummary] = useState<{ deducted: number; refunded: number } | null>(null);

  const steps = [
    { num: 1, title: '合約選擇' },
    { num: 2, title: '退租啟動' },
    { num: 3, title: '退租檢查' },
    { num: 4, title: '遙控器清點' },
    { num: 5, title: '扣款退款試算' },
    { num: 6, title: '貨櫃驗收解鎖' },
    { num: 7, title: '完成結算' }
  ];

  const handleStart = async () => {
    setLoading(true);
    setError(null);
    try {
      await startTermination({ requestId: 'REQ-TERM-' + Date.now(), contract_id: contractId });
      setCurrentStep(3);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : '啟動退租失敗');
    } finally {
      setLoading(false);
    }
  };

  const handleCalculateAndComplete = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await completeTermination({
        requestId: 'REQ-COMPLETE-' + Date.now(),
        contract_id: contractId,
        requested_date: new Date().toISOString().split('T')[0],
        actual_end_date: new Date().toISOString().split('T')[0],
        inspection_status: 'pending',
        remote_control_expected: Number(remoteExpected),
        remote_control_returned: Number(remoteReturned),
        damage_fee: Number(damageFee),
        cleaning_fee: Number(cleaningFee),
        other_fee: 0,
        deposit_original: Number(depositOriginal),
        deposit_deducted: 0,
        deposit_refunded: 0,
        status: 'completed'
      });

      setRefundSummary({
        deducted: result.deposit_deducted,
        refunded: result.deposit_refunded
      });
      setCurrentStep(6);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : '結算失敗');
    } finally {
      setLoading(false);
    }
  };

  const handleInspectionPass = async () => {
    setLoading(true);
    setError(null);
    try {
      await completeContainerInspection({
        requestId: 'REQ-INSP-' + Date.now(),
        container_id: containerId,
        inspection_status: 'passed'
      });
      setCurrentStep(7);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : '驗收解鎖失敗');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="saas-card p-6 space-y-6">
      {/* Step Indicator */}
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

      {/* Step Body */}
      <div className="min-h-[220px]">
        {currentStep === 1 && (
          <div className="space-y-4">
            <h3 className="font-bold text-base text-brand-navy-950">Step 1: 選擇退租合約與貨櫃</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-lg">
              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1">合約 ID</label>
                <input
                  type="text"
                  value={contractId}
                  onChange={(e) => setContractId(e.target.value)}
                  className="w-full saas-input"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1">貨櫃 ID</label>
                <input
                  type="text"
                  value={containerId}
                  onChange={(e) => setContainerId(e.target.value)}
                  className="w-full saas-input"
                />
              </div>
            </div>
          </div>
        )}

        {currentStep === 2 && (
          <div className="space-y-4">
            <h3 className="font-bold text-base text-brand-navy-950">Step 2: 啟動退租流程 (狀態安全校驗)</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              點選啟動後，合約狀態將變更為 <StatusBadge status="ENDING" />，對應貨櫃狀態將變更為{' '}
              <StatusBadge status="INSPECTION" />，<strong>且在現場驗收完成前不得直接轉為 AVAILABLE</strong>。
            </p>
            <button
              onClick={() => void handleStart()}
              disabled={loading}
              className="px-4 py-2 bg-status-warning text-white font-semibold text-xs rounded-lg shadow-sm"
            >
              {loading ? '啟動中...' : '確認啟動退租 (貨櫃轉為 INSPECTION)'}
            </button>
          </div>
        )}

        {currentStep === 3 && (
          <div className="space-y-4">
            <h3 className="font-bold text-base text-brand-navy-950">Step 3: 現場屋況與清潔檢查</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-lg">
              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1">預估清潔費 ($)</label>
                <input
                  type="number"
                  value={cleaningFee}
                  onChange={(e) => setCleaningFee(e.target.value)}
                  className="w-full saas-input"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1">預估損壞賠償 ($)</label>
                <input
                  type="number"
                  value={damageFee}
                  onChange={(e) => setDamageFee(e.target.value)}
                  className="w-full saas-input"
                />
              </div>
            </div>
          </div>
        )}

        {currentStep === 4 && (
          <div className="space-y-4">
            <h3 className="font-bold text-base text-brand-navy-950">Step 4: 遙控器清點與缺少扣款 ($350/個)</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-lg">
              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1">應歸還數量</label>
                <input
                  type="number"
                  value={remoteExpected}
                  onChange={(e) => setRemoteExpected(e.target.value)}
                  className="w-full saas-input"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1">實際歸還數量</label>
                <input
                  type="number"
                  value={remoteReturned}
                  onChange={(e) => setRemoteReturned(e.target.value)}
                  className="w-full saas-input"
                />
              </div>
            </div>
          </div>
        )}

        {currentStep === 5 && (
          <div className="space-y-4">
            <h3 className="font-bold text-base text-brand-navy-950">Step 5: 押金與扣款金額試算結算</h3>
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1">原押金金額 ($)</label>
              <input
                type="number"
                value={depositOriginal}
                onChange={(e) => setDepositOriginal(e.target.value)}
                className="w-full saas-input max-w-xs"
              />
            </div>
            <button
              onClick={() => void handleCalculateAndComplete()}
              disabled={loading}
              className="px-5 py-2 bg-brand-navy-950 text-white font-semibold text-xs rounded-lg shadow-sm"
            >
              {loading ? '計算中...' : '進行退租扣款與押金結算'}
            </button>
          </div>
        )}

        {currentStep === 6 && refundSummary && (
          <div className="space-y-4">
            <h3 className="font-bold text-base text-brand-navy-950">Step 6: 押金結算成功 (貨櫃解鎖準備)</h3>
            <div className="bg-surface-muted p-4 rounded-lg border border-border-default space-y-2 text-xs">
              <p><span className="text-text-secondary">原押金：</span><span className="font-bold">${depositOriginal}</span></p>
              <p><span className="text-text-secondary">總扣款：</span><span className="font-bold text-status-danger">${refundSummary.deducted}</span></p>
              <p><span className="text-text-secondary">最終應退款：</span><span className="font-bold text-lg text-brand-navy-950">${refundSummary.refunded}</span></p>
            </div>
            <p className="text-xs text-text-secondary">
              合約已變更為 <StatusBadge status="ENDED" />。貨櫃仍維持 <StatusBadge status="INSPECTION" />，請點選下方解鎖。
            </p>
            <button
              onClick={() => void handleInspectionPass()}
              disabled={loading}
              className="px-5 py-2 bg-status-success text-white font-semibold text-xs rounded-lg shadow-sm"
            >
              {loading ? '解鎖中...' : '確認現場驗收通過 (貨櫃解鎖為 AVAILABLE)'}
            </button>
          </div>
        )}

        {currentStep === 7 && (
          <div className="text-center space-y-3 py-6">
            <div className="w-12 h-12 bg-emerald-100 text-status-success rounded-full flex items-center justify-center text-2xl mx-auto">
              ✓
            </div>
            <h3 className="font-bold text-lg text-brand-navy-950">退租結算與貨櫃解鎖全流程完成！</h3>
            <div className="flex justify-center gap-2">
              <StatusBadge status="ENDED" />
              <StatusBadge status="AVAILABLE" />
            </div>
          </div>
        )}
      </div>

      {/* Buttons */}
      <div className="flex items-center justify-between pt-4 border-t border-border-default">
        {currentStep < 7 ? (
          <>
            <button
              onClick={currentStep === 1 ? onCancel : () => setCurrentStep((prev) => prev - 1)}
              className="px-4 py-2 text-xs font-semibold text-text-secondary hover:bg-surface-muted rounded-lg border border-border-default"
            >
              {currentStep === 1 ? '取消' : '上一步'}
            </button>

            {currentStep !== 2 && currentStep !== 5 && currentStep !== 6 && (
              <button
                onClick={() => setCurrentStep((prev) => prev + 1)}
                className="px-4 py-2 bg-brand-navy-950 hover:bg-brand-navy-900 text-white rounded-lg text-xs font-semibold"
              >
                下一步 ➔
              </button>
            )}
          </>
        ) : (
          <button
            onClick={onSuccess}
            className="w-full py-2.5 bg-brand-navy-950 text-white rounded-lg text-xs font-semibold"
          >
            完成並返回退租頁面
          </button>
        )}
      </div>
    </div>
  );
}
