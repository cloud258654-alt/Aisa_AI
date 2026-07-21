export default function LoadingState({ text = '資料載入中...' }: { text?: string }) {
  return (
    <div className="saas-card p-12 text-center my-6 space-y-4">
      <div className="w-10 h-10 border-4 border-brand-gold-300 border-t-brand-navy-950 rounded-full animate-spin mx-auto"></div>
      <p className="text-sm font-semibold text-text-secondary">{text}</p>
    </div>
  );
}
