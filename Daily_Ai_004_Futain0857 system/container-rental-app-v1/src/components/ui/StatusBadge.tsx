const STATUS_MAP: Record<string, { label: string; bg: string; text: string; border: string }> = {
  // Container
  AVAILABLE: { label: '空櫃 (Available)', bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  RESERVED: { label: '預訂 (Reserved)', bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
  RENTED: { label: '出租中 (Rented)', bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200' },
  INSPECTION: { label: '退租檢查中 (Inspection)', bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
  MAINTENANCE: { label: '維修中 (Maintenance)', bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-200' },
  BLOCKED: { label: '鎖定中 (Blocked)', bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' },
  RETIRED: { label: '停用 (Retired)', bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-300' },

  // Contract
  DRAFT: { label: '草稿 (Draft)', bg: 'bg-slate-100', text: 'text-slate-700', border: 'border-slate-300' },
  ACTIVE: { label: '生效中 (Active)', bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  ENDING: { label: '退租辦理中 (Ending)', bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
  ENDED: { label: '已結束 (Ended)', bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-300' },
  CANCELLED: { label: '已取消 (Cancelled)', bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200' },

  // Invoice
  UNPAID: { label: '未付款 (Unpaid)', bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200' },
  PARTIAL: { label: '部分付款 (Partial)', bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
  PAID: { label: '已結清 (Paid)', bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  VOID: { label: '已作廢 (Void)', bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-300' },

  // Payment
  CONFIRMED: { label: '已對帳 (Confirmed)', bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  REFUNDED: { label: '已退款 (Refunded)', bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' }
};

interface StatusBadgeProps {
  status: string;
  customLabel?: string;
}

export default function StatusBadge({ status, customLabel }: StatusBadgeProps) {
  const upperKey = (status || '').toString().toUpperCase();
  const config = STATUS_MAP[upperKey] || {
    label: customLabel || status,
    bg: 'bg-gray-100',
    text: 'text-gray-700',
    border: 'border-gray-300'
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${config.bg} ${config.text} ${config.border}`}
    >
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current opacity-75"></span>
      {customLabel || config.label}
    </span>
  );
}
