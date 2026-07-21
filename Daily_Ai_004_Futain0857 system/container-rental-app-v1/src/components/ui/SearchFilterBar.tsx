import React from 'react';

interface FilterOption {
  value: string;
  label: string;
}

interface FilterSelect {
  id: string;
  label: string;
  value: string;
  onChange: (val: string) => void;
  options: FilterOption[];
}

interface SearchFilterBarProps {
  searchValue: string;
  onSearchChange: (val: string) => void;
  placeholder?: string;
  filters?: FilterSelect[];
  rightAction?: React.ReactNode;
}

export default function SearchFilterBar({
  searchValue,
  onSearchChange,
  placeholder = '搜尋關鍵字...',
  filters = [],
  rightAction
}: SearchFilterBarProps) {
  return (
    <div className="saas-card p-4 mb-6 space-y-3 sm:space-y-0 sm:flex sm:items-center sm:justify-between gap-4">
      {/* Search Input */}
      <div className="flex-1 flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <span className="absolute left-3 top-2.5 text-text-secondary text-sm">🔍</span>
          <input
            type="text"
            value={searchValue}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder={placeholder}
            className="w-full pl-9 pr-3 py-2 saas-input text-sm"
          />
        </div>

        {/* Filter Dropdowns */}
        {filters.map((filter) => (
          <div key={filter.id} className="shrink-0 hidden md:block">
            <select
              value={filter.value}
              onChange={(e) => filter.onChange(e.target.value)}
              className="saas-input py-2 text-xs font-medium"
            >
              {filter.options.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        ))}
      </div>

      {rightAction && <div className="shrink-0 flex items-center gap-2">{rightAction}</div>}
    </div>
  );
}
