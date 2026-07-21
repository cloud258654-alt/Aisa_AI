interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  isDangerous?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmText = '確認執行',
  cancelText = '取消',
  isDangerous = true,
  onConfirm,
  onCancel
}: ConfirmDialogProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div onClick={onCancel} className="fixed inset-0 bg-brand-navy-950/60 backdrop-blur-xs"></div>

      {/* Modal */}
      <div className="relative w-full max-w-md saas-card p-6 shadow-2xl z-10 space-y-4 animate-fade-in">
        <div className="flex items-center gap-3">
          <div
            className={`w-10 h-10 rounded-full flex items-center justify-center text-lg shrink-0 ${
              isDangerous ? 'bg-rose-100 text-status-danger' : 'bg-blue-100 text-status-info'
            }`}
          >
            {isDangerous ? '⚠️' : '❓'}
          </div>
          <div>
            <h3 className="font-bold text-lg text-brand-navy-950">{title}</h3>
            <p className="text-xs text-text-secondary mt-0.5">二次安全性確認操作</p>
          </div>
        </div>

        <p className="text-sm text-text-primary leading-relaxed bg-surface-muted p-3.5 rounded-lg border border-border-default">
          {message}
        </p>

        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-xs font-semibold text-text-secondary hover:text-text-primary hover:bg-surface-muted rounded-lg border border-border-default transition-all"
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            className={`px-4 py-2 text-xs font-semibold text-white rounded-lg shadow-sm transition-all ${
              isDangerous
                ? 'bg-status-danger hover:bg-rose-700'
                : 'bg-brand-navy-950 hover:bg-brand-navy-900'
            }`}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
