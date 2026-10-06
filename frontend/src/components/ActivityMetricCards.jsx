import React from 'react';
import { Droplets, Flame } from 'lucide-react';

function ActivityMetricCards({ streakDays = 0, waterGlasses = 12, onWaterClick }) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:gap-4 mb-4">
      <article className="bg-white rounded-[26px] p-4 sm:p-5 shadow-xs border border-gray-100/60 flex flex-col justify-between">
        <div className="flex items-start justify-between mb-4">
          <h4 className="text-[14px] sm:text-[15px] font-bold text-gray-900 leading-tight">
            Meal logging<br />streak
          </h4>
          <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-orange-50 flex items-center justify-center text-orange-500">
            <Flame className="w-4 h-4" aria-hidden="true" />
          </div>
        </div>
        <div className="flex items-baseline">
          <span className="text-[22px] sm:text-[24px] font-extrabold text-gray-950 tracking-tight">
            {streakDays}
          </span>
          <span className="text-[12px] sm:text-[13px] font-medium text-gray-400 ml-1.5">
            {streakDays === 1 ? 'day' : 'days'}
          </span>
        </div>
        <span className="mt-2 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
          {streakDays > 0 ? 'Current streak' : 'Log a meal to start'}
        </span>
      </article>

      <button
        type="button"
        onClick={onWaterClick}
        className="text-left bg-white rounded-[26px] p-4 sm:p-5 shadow-xs border border-gray-100/60 flex flex-col justify-between hover:border-gray-200 transition-all cursor-pointer group"
      >
        <div className="flex items-start justify-between mb-4 w-full">
          <h4 className="text-[14px] sm:text-[15px] font-bold text-gray-900 leading-tight">
            Drink<br />water
          </h4>
          <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-gray-50/90 group-hover:bg-gray-100 flex items-center justify-center text-gray-700 transition-colors">
            <Droplets className="w-4 h-4" aria-hidden="true" />
          </div>
        </div>
        <div className="flex items-baseline">
          <span className="text-[22px] sm:text-[24px] font-extrabold text-gray-950 tracking-tight">
            {waterGlasses}
          </span>
          <span className="text-[12px] sm:text-[13px] font-medium text-gray-400 ml-1.5">
            glasses
          </span>
        </div>
      </button>
    </div>
  );
}

export default ActivityMetricCards;
