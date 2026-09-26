import React, { useState } from 'react';
import { Flame } from 'lucide-react';

function WeeklyCalorieBarChart({
  currentCalories = 1250,
  targetCalories = 1920,
}) {
  const [selectedDayIndex, setSelectedDayIndex] = useState(3); // Default to Wed (index 3)

  const weeklyData = [
    { day: 'Sun', percentage: 55, calories: 1050, label: '55%' },
    { day: 'Mon', percentage: 70, calories: 1340, label: '70%' },
    { day: 'Tue', percentage: 45, calories: 860, label: '45%' },
    { day: 'Wed', percentage: 88, calories: 1250, label: '120%' },
    { day: 'Thu', percentage: 65, calories: 1240, label: '65%' },
    { day: 'Fri', percentage: 48, calories: 920, label: '48%' },
    { day: 'Sat', percentage: 75, calories: 1440, label: '75%' },
  ];

  return (
    <div className="w-full bg-white rounded-[28px] p-5 sm:p-6 mb-4 shadow-xs border border-gray-100/60 select-none">
      {/* Top Header: Current Calories & Target Calories */}
      <div className="flex items-center justify-between mb-4 px-1">
        <div className="flex items-center gap-1.5 text-gray-950">
          <Flame className="w-5 h-5 fill-gray-950 stroke-none" />
          <span className="text-[20px] font-extrabold tracking-tight">
            {currentCalories}
          </span>
          <span className="text-[13px] font-medium text-gray-500 ml-0.5">
            kcal
          </span>
        </div>

        <div className="text-[13px] text-gray-400 font-medium">
          Target:{' '}
          <strong className="text-gray-900 font-bold ml-1">
            {targetCalories} kcal
          </strong>
        </div>
      </div>

      {/* Bar Chart Container */}
      <div className="pt-8 pb-1">
        <div className="grid grid-cols-7 gap-2 sm:gap-2.5 items-end h-[145px]">
          {weeklyData.map((item, index) => {
            const isSelected = index === selectedDayIndex;

            return (
              <div
                key={item.day}
                onClick={() => setSelectedDayIndex(index)}
                className="flex flex-col items-center h-full justify-end cursor-pointer group relative"
              >
                {/* Floating Tooltip Badge for Active Day */}
                {isSelected && (
                  <div className="absolute -top-7 left-1/2 -translate-x-1/2 z-10 animate-fade-in flex flex-col items-center">
                    <div className="bg-black text-white text-[10px] font-bold px-2 py-0.5 rounded-full shadow-md tracking-tight whitespace-nowrap">
                      {item.label}
                    </div>
                    {/* Tooltip Downward Caret */}
                    <div className="w-0 h-0 border-x-[3px] border-x-transparent border-t-[4px] border-t-black -mt-[0.5px]" />
                  </div>
                )}

                {/* Vertical Capsule Pill Bar */}
                <div className="w-full max-w-[34px] h-[115px] rounded-full overflow-hidden bg-striped-pattern flex flex-col justify-end p-0.5 border border-gray-100/70 transition-transform duration-200 group-hover:scale-102">
                  <div
                    className={`w-full rounded-full transition-all duration-500 ease-out ${
                      isSelected
                        ? 'bg-gradient-to-t from-[#84cc16] via-[#bef264] to-[#dcfce7] shadow-xs'
                        : 'bg-[#f0f2f4] group-hover:bg-[#e4e7ec]'
                    }`}
                    style={{ height: `${item.percentage}%` }}
                  />
                </div>

                {/* Day Label */}
                <span
                  className={`text-[11px] sm:text-[12px] mt-2.5 transition-colors ${
                    isSelected
                      ? 'font-bold text-gray-950'
                      : 'font-medium text-gray-400 group-hover:text-gray-600'
                  }`}
                >
                  {item.day}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default WeeklyCalorieBarChart;
