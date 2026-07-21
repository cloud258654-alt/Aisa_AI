import React from 'react';

interface KeyValueField {
  label: string;
  value: React.ReactNode;
}

interface MobileRecordCardProps {
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  badge?: React.ReactNode;
  fields: KeyValueField[];
  actionButtons?: React.ReactNode;
  onClick?: () => void;
}

export default function MobileRecordCard({
  title,
  subtitle,
  badge,
  fields,
  actionButtons,
  onClick
}: MobileRecordCardProps) {
  return (
    <div
      onClick={onClick}
      className={`md:hidden saas-card p-4 space-y-3 ${onClick ? 'cursor-pointer active:bg-surface-muted' : ''}`}
    >
      <div className="flex items-start justify-between gap-2 border-b border-border-default pb-2.5">
        <div>
          <div className="font-bold text-base text-brand-navy-950">{title}</div>
          {subtitle && <div className="text-xs text-text-secondary mt-0.5">{subtitle}</div>}
        </div>
        {badge && <div className="shrink-0">{badge}</div>}
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs">
        {fields.map((field, idx) => (
          <div key={idx} className="space-y-0.5">
            <span className="text-text-secondary block font-medium">{field.label}</span>
            <span className="text-text-primary font-semibold block">{field.value}</span>
          </div>
        ))}
      </div>

      {actionButtons && (
        <div className="pt-2 border-t border-border-default flex items-center justify-end gap-2">
          {actionButtons}
        </div>
      )}
    </div>
  );
}
