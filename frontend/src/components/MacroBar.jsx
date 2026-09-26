import React from 'react';
import { formatGrams, formatMg } from '../utils/formatters';

function MacroBar({
  label,
  current = 0,
  target = 100,
  unit = 'g',
  colorClass = 'bg-indigo-600',
  trackClass = 'bg-indigo-50',
  icon: Icon,
}) {
  const percentage = Math.min(100, Math.round((current / target) * 100));
  const formatVal = unit === 'mg' ? formatMg : formatGrams;

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-xs font-semibold">
        <div className="flex items-center gap-1.5 text-gray-700">
          {Icon && <Icon className="w-3.5 h-3.5 text-gray-400" />}
          <span>{label}</span>
        </div>
        <div className="text-gray-500 font-medium">
          <strong className="text-gray-900">{formatVal(current)}</strong>
          <span className="text-gray-400"> / {formatVal(target)}</span>
          <span className="ml-1.5 text-[11px] font-bold text-gray-400">({percentage}%)</span>
        </div>
      </div>

      <div className={`h-2.5 w-full rounded-full ${trackClass} overflow-hidden`}>
        <div
          className={`h-full rounded-full transition-all duration-700 ease-out ${colorClass}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

export default MacroBar;
