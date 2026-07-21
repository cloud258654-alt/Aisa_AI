import React, { useState } from 'react';
import { startTermination, completeTermination, completeContainerInspection } from '../services/api/terminationsApi';

export default function TerminationPage() {
  const [contractId, setContractId] = useState('');
  const [remoteExpected, setRemoteExpected] = useState('1');
  const [remoteReturned, setRemoteReturned] = useState('0');
  const [cleaningFee, setCleaningFee] = useState('1000');
  const [damageFee, setDamageFee] = useState('0');
  const [depositOriginal, setDepositOriginal] = useState('10000');
  const [containerId, setContainerId] = useState('');

  const [stepLog, setStepLog] = useState<string[]>([]);
  const [refundResult, setRefundResult] = useState<{ deducted: number; refunded: number } | null>(null);

  const handleStartTermination = async () => {
    try {
      const res = await startTermination({ contract_id: contractId });
      setStepLog((prev) => [...prev, `[Step 1 & 2] 合約 status -> ending, 貨櫃 status -> inspection (${res.containers_in_inspection.join(', ')})`]);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : '啟動退租失敗');
    }
  };

  const handleCompleteTermination = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = await completeTermination({
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

      setRefundResult({
        deducted: result.deposit_deducted,
        refunded: result.deposit_refunded
      });

      setStepLog((prev) => [
        ...prev,
        `[Step 3-6] 結算完成: 押金扣款 $${result.deposit_deducted}, 應退金額 $${result.deposit_refunded} (貨櫃仍保留在 inspection 狀態)`
      ]);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : '結算失敗');
    }
  };

  const handlePassInspection = async () => {
    if (!containerId) {
      alert('請輸入貨櫃 ID');
      return;
    }
    try {
      const updated = await completeContainerInspection({
        container_id: containerId,
        inspection_status: 'passed'
      });
      setStepLog((prev) => [...prev, `[Step 7 驗收完成] 貨櫃 ${updated.container_id} 狀態由 inspection 轉為 available`]);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : '驗收失敗');
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6 text-slate-100">
      <h1 className="text-2xl font-bold">退租與押金結算 Wizard (Termination & Inspection)</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-4 bg-slate-900 rounded-lg space-y-4 border border-slate-800">
          <h2 className="text-lg font-semibold text-amber-400">Step 1: 選擇退租合約與啟動檢查</h2>
          <input
            type="text"
            placeholder="合約 ID (e.g. CNT-001)"
            value={contractId}
            onChange={(e) => setContractId(e.target.value)}
            className="w-full p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
          />
          <button
            onClick={() => void handleStartTermination()}
            className="w-full py-2 bg-amber-600 hover:bg-amber-500 rounded text-white font-medium"
          >
            啟動退租 (貨櫃進入 INSPECTION)
          </button>
        </div>

        <form onSubmit={handleCompleteTermination} className="p-4 bg-slate-900 rounded-lg space-y-4 border border-slate-800">
          <h2 className="text-lg font-semibold text-cyan-400">Step 2: 7-Step 押金費用試算與結算</h2>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-slate-400">應還遙控器</label>
              <input
                type="number"
                value={remoteExpected}
                onChange={(e) => setRemoteExpected(e.target.value)}
                className="w-full p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400">實還遙控器</label>
              <input
                type="number"
                value={remoteReturned}
                onChange={(e) => setRemoteReturned(e.target.value)}
                className="w-full p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400">清潔費 ($1000)</label>
              <input
                type="number"
                value={cleaningFee}
                onChange={(e) => setCleaningFee(e.target.value)}
                className="w-full p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400">損壞修繕費</label>
              <input
                type="number"
                value={damageFee}
                onChange={(e) => setDamageFee(e.target.value)}
                className="w-full p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
              />
            </div>
          </div>
          <div>
            <label className="text-xs text-slate-400">原押金金額 ($10000)</label>
            <input
              type="number"
              value={depositOriginal}
              onChange={(e) => setDepositOriginal(e.target.value)}
              className="w-full p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
            />
          </div>
          <button type="submit" className="w-full py-2 bg-cyan-600 hover:bg-cyan-500 rounded text-white font-medium">
            進行退租結算
          </button>
        </form>
      </div>

      {refundResult && (
        <div className="p-4 bg-emerald-950/80 border border-emerald-700 rounded-lg text-emerald-200">
          <h3 className="font-bold text-lg">退租結算結果 (Case D 驗證)</h3>
          <p>原押金：${depositOriginal}</p>
          <p>總扣款金額 (遙控器+清潔費+損壞)：${refundResult.deducted}</p>
          <p className="text-xl font-extrabold text-amber-300">最終應退款金額：${refundResult.refunded}</p>
        </div>
      )}

      <div className="p-4 bg-slate-900 rounded-lg space-y-4 border border-slate-800">
        <h2 className="text-lg font-semibold text-emerald-400">Step 3: 貨櫃現場檢查與狀態解鎖 (Inspection 轉至 Available)</h2>
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="貨櫃 ID (e.g. CONT-CASE-A)"
            value={containerId}
            onChange={(e) => setContainerId(e.target.value)}
            className="flex-1 p-2 bg-slate-950 border border-slate-700 rounded text-slate-100"
          />
          <button
            onClick={() => void handlePassInspection()}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded text-white font-medium"
          >
            完成檢查 (轉為 AVAILABLE)
          </button>
        </div>
      </div>

      <div className="p-4 bg-slate-950 rounded-lg border border-slate-800">
        <h3 className="text-sm font-semibold text-slate-400 mb-2">流程狀態紀錄 Log:</h3>
        <ul className="space-y-1 font-mono text-xs text-slate-300">
          {stepLog.map((log, idx) => (
            <li key={idx}>• {log}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
