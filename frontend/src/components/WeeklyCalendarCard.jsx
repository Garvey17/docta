import React, { useState } from 'react';
import { ArrowLeft, ArrowRight } from 'lucide-react';

function WeeklyCalendarCard() {
  const [selectedDayIndex, setSelectedDayIndex] = useState(3); // Default Wed 15

  const days = [
    { day: 'Sun', date: 12 },
    { day: 'Mon', date: 13 },
    { day: 'Tue', date: 14 },
    { day: 'Wed', date: 15 },
    { day: 'Thu', date: 16 },
    { day: 'Thu', date: 16 },
    { day: 'Fri', date: 17 },
  ];

  return (
    <div className="w-full bg-[#e3f79e] rounded-[28px] p-5 mb-4 shadow-xs select-none">
      {/* Top Header: Month & Navigation Arrows */}
      <div className="flex items-center justify-between mb-4 px-1">
        <h2 className="text-[17px] font-bold text-gray-900 tracking-tight">
          November 2025
        </h2>

        <div className="flex items-center gap-1.5">
          <button
            type="button"
            aria-label="Previous week"
            className="w-8 h-8 rounded-full bg-white/90 hover:bg-white flex items-center justify-center text-gray-800 shadow-2xs transition-all active:scale-95"
          >
            <ArrowLeft className="w-3.5 h-3.5 stroke-[2.2]" />
          </button>
          <button
            type="button"
            aria-label="Next week"
            className="w-8 h-8 rounded-full bg-white/90 hover:bg-white flex items-center justify-center text-gray-800 shadow-2xs transition-all active:scale-95"
          >
            <ArrowRight className="w-3.5 h-3.5 stroke-[2.2]" />
          </button>
        </div>
      </div>

      {/* Days & Date Circles Row */}
      <div className="grid grid-cols-7 gap-1 text-center">
        {days.map((item, index) => {
          const isSelected = index === selectedDayIndex;
          return (
            <div
              key={`${item.day}-${index}`}
              onClick={() => setSelectedDayIndex(index)}
              className="flex flex-col items-center gap-2 cursor-pointer group"
            >
              {/* Day Label */}
              <span
                className={`text-[12px] font-medium transition-colors ${
                  isSelected ? 'text-gray-900 font-bold' : 'text-gray-700/80 group-hover:text-gray-900'
                }`}
              >
                {item.day}
              </span>

              {/* Date Circle Pill */}
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center text-[13px] font-semibold transition-all duration-200 ${
                  isSelected
                    ? 'bg-[#d0ed7e] border-2 border-[#82b826] text-gray-950 font-bold shadow-xs scale-105'
                    : 'bg-white/95 text-gray-800 group-hover:bg-white shadow-2xs group-hover:scale-102'
                }`}
              >
                {item.date}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default WeeklyCalendarCard;
