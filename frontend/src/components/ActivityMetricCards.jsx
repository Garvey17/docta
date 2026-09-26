import React from 'react';
import { Footprints, Droplets, ArrowUpRight } from 'lucide-react';

function ActivityMetricCards({
  steps = 5234,
  waterGlasses = 12,
  onStepClick,
  onWaterClick,
}) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:gap-4 mb-4">
      {/* Step to walk Card */}
      <div
        onClick={onStepClick}
        className="bg-white rounded-[26px] p-4 sm:p-5 shadow-xs border border-gray-100/60 flex flex-col justify-between hover:border-gray-200 transition-all cursor-pointer group"
      >
        <div className="flex items-start justify-between mb-4">
          <h4 className="text-[14px] sm:text-[15px] font-bold text-gray-900 leading-tight">
            Step to<br />walk
          </h4>

          {/* Circular Walking Icon Button */}
          <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-gray-50/90 group-hover:bg-gray-100 flex items-center justify-center text-gray-700 transition-colors">
            <svg
              className="w-4 h-4 text-gray-800"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="12" cy="5" r="2" />
              <path d="M10 22l2-7 3 2v5" />
              <path d="M7 13l3-2 3 2 4-3" />
            </svg>
          </div>
        </div>

        {/* Step Counter Value */}
        <div className="flex items-baseline">
          <span className="text-[22px] sm:text-[24px] font-extrabold text-gray-950 tracking-tight">
            {steps.toLocaleString()}
          </span>
          <span className="text-[12px] sm:text-[13px] font-medium text-gray-400 ml-1.5">
            step
          </span>
        </div>
      </div>

      {/* Drink water Card */}
      <div
        onClick={onWaterClick}
        className="bg-white rounded-[26px] p-4 sm:p-5 shadow-xs border border-gray-100/60 flex flex-col justify-between hover:border-gray-200 transition-all cursor-pointer group"
      >
        <div className="flex items-start justify-between mb-4">
          <h4 className="text-[14px] sm:text-[15px] font-bold text-gray-900 leading-tight">
            Drink<br />water
          </h4>

          {/* Circular Drink/Water Icon Button */}
          <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-gray-50/90 group-hover:bg-gray-100 flex items-center justify-center text-gray-700 transition-colors">
            <svg
              className="w-4 h-4 text-gray-800"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M6 3h12l-1.5 15a3 3 0 0 1-3 3h-3a3 3 0 0 1-3-3L6 3z" />
              <path d="M6 8h12" />
            </svg>
          </div>
        </div>

        {/* Water Glasses Value */}
        <div className="flex items-baseline">
          <span className="text-[22px] sm:text-[24px] font-extrabold text-gray-950 tracking-tight">
            {waterGlasses}
          </span>
          <span className="text-[12px] sm:text-[13px] font-medium text-gray-400 ml-1.5">
            glass
          </span>
        </div>
      </div>
    </div>
  );
}

export default ActivityMetricCards;
