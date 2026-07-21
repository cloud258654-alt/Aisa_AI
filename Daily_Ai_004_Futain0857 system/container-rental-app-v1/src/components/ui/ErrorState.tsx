interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export default function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="saas-card p-8 text-center my-6 border-status-danger/30 bg-rose-50/50 space-y-3">
      <span className="text-3xl block">⚠️</span>
      <h4 className="text-base font-bold text-status-danger">系統發生錯誤或連線異常</h4>
      <p className="text-xs sm:text-sm text-text-secondary leading-relaxed max-w-md mx-auto">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-brand-navy-950 hover:bg-brand-navy-900 text-white rounded-lg text-xs font-semibold shadow-sm transition-all"
        >
          重新嘗試載入
        </button>
      )}
    </div>
  );
}
