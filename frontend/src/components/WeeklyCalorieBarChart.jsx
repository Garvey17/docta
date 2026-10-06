import React, { useState } from 'react';
import { Flame } from 'lucide-react';

function WeeklyCalorieBarChart({
  currentCalories = 0,
  targetCalories = 2200,
  weeklyData = null,
}) {
  const defaultWeeklyData = [
    { day: 'Sun', percentage: 10, calories: 0, label: '0%' },
    { day: 'Mon', percentage: 10, calories: 0, label: '0%' },
    { day: 'Tue', percentage: 10, calories: 0, label: '0%' },
    { day: 'Wed', percentage: 10, calories: 0, label: '0%' },
    { day: 'Thu', percentage: 10, calories: 0, label: '0%' },
    { day: 'Fri', percentage: 10, calories: 0, label: '0%' },
    { day: 'Sat', percentage: 10, calories: 0, label: '0%' },
  ];

  const dataToRender = weeklyData || defaultWeeklyData;
  const [selectedDayIndex, setSelectedDayIndex] = useState(new Date().getDay());
  const selectedDay = dataToRender[selectedDayIndex];
  const displayedCalories = selectedDay?.calories ?? currentCalories;

  return (
    <div className="w-full bg-white rounded-[28px] p-5 sm:p-6 mb-4 shadow-xs border border-gray-100/60 select-none">
      {/* Selected day calories & daily target */}
      <div className="flex items-center justify-between mb-4 px-1">
        <div className="flex items-center gap-1.5 text-gray-950">
          <Flame className="w-5 h-5 fill-gray-950 stroke-none" />
          <span className="text-[20px] font-extrabold tracking-tight">
            {displayedCalories}
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
          {dataToRender.map((item, index) => {
            const isSelected = index === selectedDayIndex;

            return (
              <div
                key={item.day}
                role="button"
                tabIndex={0}
                aria-label={`${item.day}${item.date ? `, ${new Date(item.date).toLocaleDateString()}` : ''}: ${item.calories} calories`}
                aria-pressed={isSelected}
                onClick={() => setSelectedDayIndex(index)}
                onKeyDown={(event) => {
                  if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    setSelectedDayIndex(index);
                  }
                }}
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
                        : 'bg-[#cbd5e1] group-hover:bg-[#94a3b8]'
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
