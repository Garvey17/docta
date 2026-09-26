import React from 'react';
import { ArrowUpRight } from 'lucide-react';

function HeartRateCard({
  rate = 140,
  unit = 'bpm',
  status = 'Higher than usual',
  onDetailsClick,
}) {
  return (
    <div className="w-full bg-white rounded-[28px] p-5 sm:p-6 mb-4 shadow-xs border border-gray-100/60 select-none">
      {/* Top Row: Title, Subtitle & Action Button */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-[18px] font-bold text-gray-900 tracking-tight">
            Heart Rate
          </h3>
          <p className="text-[12px] text-gray-400 font-medium mt-0.5">
            {status}
          </p>
        </div>

        {/* Circular Action Button */}
        <button
          type="button"
          onClick={onDetailsClick}
          aria-label="Heart rate details"
          className="w-9 h-9 rounded-full bg-gray-50 hover:bg-gray-100 flex items-center justify-center text-gray-700 transition-transform active:scale-95 shadow-2xs"
        >
          <ArrowUpRight className="w-4 h-4 stroke-[2.2]" />
        </button>
      </div>

      {/* Bottom Row: BPM Metric & ECG Pulse Wave */}
      <div className="flex items-end justify-between gap-4 pt-1">
        {/* BPM Counter */}
        <div className="flex items-baseline">
          <span className="text-[30px] sm:text-[32px] font-extrabold text-gray-950 tracking-tight leading-none">
            {rate}
          </span>
          <span className="text-[13px] font-medium text-gray-400 ml-1.5">
            {unit}
          </span>
        </div>

        {/* ECG Pulse Wave SVG */}
        <div className="flex-1 max-w-[180px] sm:max-w-[200px] h-12 flex items-center">
          <svg
            className="w-full h-full overflow-visible"
            viewBox="0 0 170 50"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M 0 25 L 35 25 L 44 14 L 54 34 L 64 6 L 76 48 L 88 25 L 105 15 L 115 32 L 124 25 L 170 25"
              stroke="#f05a3e"
              strokeWidth="2.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
      </div>
    </div>
  );
}

export default HeartRateCard;
