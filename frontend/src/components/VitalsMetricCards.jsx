import React from 'react';
import { ArrowUpRight } from 'lucide-react';

function VitalsMetricCards({
  bloodPressure = 120,
  bloodPressureUnit = 'bpm',
  glucoseLevel = 88,
  glucoseUnit = 'mg',
  onBpClick,
  onGlucoseClick,
}) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:gap-4 mb-4 select-none">
      {/* Blood Pressure Card */}
      <div
        onClick={onBpClick}
        className="bg-white rounded-[26px] p-4 sm:p-5 shadow-xs border border-gray-100/60 flex flex-col justify-between hover:border-gray-200 transition-all cursor-pointer group"
      >
        <div className="flex items-start justify-between mb-4">
          <h4 className="text-[14px] sm:text-[15px] font-bold text-gray-900 leading-tight">
            Blood<br />Pressure
          </h4>

          {/* Circular Action Button */}
          <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-gray-50/90 group-hover:bg-gray-100 flex items-center justify-center text-gray-700 transition-colors">
            <ArrowUpRight className="w-4 h-4 stroke-[2.2]" />
          </div>
        </div>

        {/* Blood Pressure Value */}
        <div className="flex items-baseline">
          <span className="text-[24px] sm:text-[26px] font-extrabold text-gray-950 tracking-tight">
            {bloodPressure}
          </span>
          <span className="text-[12px] sm:text-[13px] font-medium text-gray-400 ml-1.5">
            {bloodPressureUnit}
          </span>
        </div>
      </div>

      {/* Glucose Level Card */}
      <div
        onClick={onGlucoseClick}
        className="bg-white rounded-[26px] p-4 sm:p-5 shadow-xs border border-gray-100/60 flex flex-col justify-between hover:border-gray-200 transition-all cursor-pointer group"
      >
        <div className="flex items-start justify-between mb-4">
          <h4 className="text-[14px] sm:text-[15px] font-bold text-gray-900 leading-tight">
            Glucose<br />Level
          </h4>

          {/* Circular Action Button */}
          <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-gray-50/90 group-hover:bg-gray-100 flex items-center justify-center text-gray-700 transition-colors">
            <ArrowUpRight className="w-4 h-4 stroke-[2.2]" />
          </div>
        </div>

        {/* Glucose Level Value */}
        <div className="flex items-baseline">
          <span className="text-[24px] sm:text-[26px] font-extrabold text-gray-950 tracking-tight">
            {glucoseLevel}
          </span>
          <span className="text-[12px] sm:text-[13px] font-medium text-gray-400 ml-1.5">
            {glucoseUnit}
          </span>
        </div>
      </div>
    </div>
  );
}

export default VitalsMetricCards;
