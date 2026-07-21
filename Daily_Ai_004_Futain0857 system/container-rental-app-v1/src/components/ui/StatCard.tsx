import React from 'react';
import { Link } from 'react-router-dom';

interface StatCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  subtext?: string;
  trend?: string;
  trendType?: 'positive' | 'negative' | 'neutral';
  linkTo?: string;
}

export default function StatCard({
  title,
  value,
  icon,
  subtext,
  trend,
  trendType = 'neutral',
  linkTo
}: StatCardProps) {
  const getTrendBadge = () => {
    if (!trend) return null;
    let bg = 'bg-surface-muted text-text-secondary border-border-default';
    if (trendType === 'positive') bg = 'bg-emerald-50 text-status-success border-emerald-200';
    if (trendType === 'negative') bg = 'bg-rose-50 text-status-danger border-rose-200';

    return (
      <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${bg}`}>
        {trend}
      </span>
    );
  };

  const CardContent = (
    <div className="saas-card p-5 space-y-3 relative overflow-hidden group hover:border-brand-navy-950/30 transition-all duration-200">
      <div className="flex justify-between items-start">
        <span className="text-xs font-bold text-text-secondary tracking-wide uppercase">{title}</span>
        {icon && (
          <div className="p-2.5 rounded-xl bg-surface-muted border border-border-default text-brand-navy-950 shadow-xs">
            {icon}
          </div>
        )}
      </div>

      <div className="flex items-baseline justify-between">
        <h3 className="text-2xl sm:text-3xl font-extrabold text-brand-navy-950 tracking-tight">{value}</h3>
        {getTrendBadge()}
      </div>

      {subtext && <p className="text-xs text-text-secondary font-medium">{subtext}</p>}
    </div>
  );

  if (linkTo) {
    return <Link to={linkTo}>{CardContent}</Link>;
  }

  return CardContent;
}
