import React from 'react';

interface EmptyStateProps {
  title?: string;
  description?: string;
  actionButton?: React.ReactNode;
}

export default function EmptyState({
  title = '尚無相關紀錄',
  description = '點選上方按鈕新增第一筆資料以進行營運追蹤。',
  actionButton
}: EmptyStateProps) {
  return (
    <div className="saas-card p-12 text-center my-6 space-y-4">
      <div className="w-16 h-16 rounded-full bg-surface-muted mx-auto flex items-center justify-center text-3xl">
        📭
      </div>
      <div>
        <h3 className="text-lg font-bold text-brand-navy-950">{title}</h3>
        <p className="text-xs sm:text-sm text-text-secondary mt-1 max-w-sm mx-auto">{description}</p>
      </div>
      {actionButton && <div className="pt-2">{actionButton}</div>}
    </div>
  );
}
