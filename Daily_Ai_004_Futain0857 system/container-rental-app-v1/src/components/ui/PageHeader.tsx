import React from 'react';

interface PageHeaderProps {
  title: string;
  description?: string;
  actionButton?: React.ReactNode;
}

export default function PageHeader({ title, description, actionButton }: PageHeaderProps) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-border-default">
      <div>
        <h1 className="text-xl sm:text-2xl font-extrabold text-brand-navy-950 tracking-tight">{title}</h1>
        {description && <p className="text-xs sm:text-sm text-text-secondary mt-1">{description}</p>}
      </div>
      {actionButton && <div className="flex items-center gap-3 shrink-0">{actionButton}</div>}
    </div>
  );
}
