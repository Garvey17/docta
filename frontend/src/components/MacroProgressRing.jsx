import React from 'react';
import { Flame } from 'lucide-react';
import { formatCalories } from '../utils/formatters';

function MacroProgressRing({
  current = 1380,
  target = 2200,
  size = 180,
  strokeWidth = 14,
  label = 'Daily Calories',
}) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const percentage = Math.min(100, Math.round((current / target) * 100));
  const offset = circumference - (percentage / 100) * circumference;

  const strokeColor = percentage >= 100
    ? '#EF4444' // Rose if over target
    : percentage >= 85
    ? '#F59E0B' // Amber if nearing target
    : '#5B50E5'; // Brand Indigo

  const remaining = Math.max(0, target - current);

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          {/* Track Circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#EEF2FF"
            strokeWidth={strokeWidth}
          />
          {/* Animated Progress Circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        {/* Center Content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-2">
          <div className="flex items-center gap-1 text-indigo-600 mb-0.5">
            <Flame className="w-4 h-4 fill-indigo-600 text-indigo-600" />
            <span className="text-xs font-bold uppercase tracking-wider">{percentage}%</span>
          </div>
          <span className="text-2xl font-extrabold text-gray-900 tracking-tight">
            {formatCalories(current)}
          </span>
          <span className="text-[11px] font-medium text-gray-400">
            of {formatCalories(target)}
          </span>
        </div>
      </div>

      <div className="mt-3 text-center">
        <span className="text-xs font-semibold text-gray-700 block">{label}</span>
        <span className="text-[11px] text-gray-500 font-medium">
          {remaining > 0 ? `${formatCalories(remaining)} remaining` : 'Target reached'}
        </span>
      </div>
    </div>
  );
}

export default MacroProgressRing;
