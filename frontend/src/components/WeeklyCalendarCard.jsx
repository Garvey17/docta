import React, { useState } from 'react';
import { ArrowLeft, ArrowRight } from 'lucide-react';

function startOfWeek(date) {
  const weekStart = new Date(date);
  weekStart.setHours(0, 0, 0, 0);
  weekStart.setDate(weekStart.getDate() - weekStart.getDay());
  return weekStart;
}

function addDays(date, amount) {
  const nextDate = new Date(date);
  nextDate.setDate(nextDate.getDate() + amount);
  return nextDate;
}

function sameDay(first, second) {
  return first.getFullYear() === second.getFullYear()
    && first.getMonth() === second.getMonth()
    && first.getDate() === second.getDate();
}

function WeeklyCalendarCard({ selectedDate = new Date(), onDateChange }) {
  const weekStart = startOfWeek(selectedDate);
  const days = Array.from({ length: 7 }, (_, index) => addDays(weekStart, index));
  const monthLabel = selectedDate.toLocaleDateString(undefined, {
    month: 'long',
    year: 'numeric',
  });

  return (
    <section
      className="w-full bg-[#e3f79e] rounded-[28px] p-5 mb-4 shadow-xs select-none"
      aria-label="Choose a dashboard date"
    >
      <div className="flex items-center justify-between mb-4 px-1">
        <h2 className="text-[17px] font-bold text-gray-900 tracking-tight" aria-live="polite">
          {monthLabel}
        </h2>

        <div className="flex items-center gap-1.5">
          <button
            type="button"
            aria-label="Previous week"
            onClick={() => onDateChange?.(addDays(selectedDate, -7))}
            className="w-8 h-8 rounded-full bg-white/90 hover:bg-white flex items-center justify-center text-gray-800 shadow-2xs transition-all active:scale-95"
          >
            <ArrowLeft className="w-3.5 h-3.5 stroke-[2.2]" />
          </button>
          <button
            type="button"
            aria-label="Next week"
            onClick={() => onDateChange?.(addDays(selectedDate, 7))}
            className="w-8 h-8 rounded-full bg-white/90 hover:bg-white flex items-center justify-center text-gray-800 shadow-2xs transition-all active:scale-95"
          >
            <ArrowRight className="w-3.5 h-3.5 stroke-[2.2]" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-1 text-center">
        {days.map((date) => {
          const isSelected = sameDay(date, selectedDate);
          const dayName = date.toLocaleDateString(undefined, { weekday: 'short' });
          const accessibleDate = date.toLocaleDateString(undefined, {
            weekday: 'long',
            month: 'long',
            day: 'numeric',
            year: 'numeric',
          });

          return (
            <button
              key={date.toISOString()}
              type="button"
              aria-label={accessibleDate}
              aria-pressed={isSelected}
              onClick={() => onDateChange?.(date)}
              className="flex flex-col items-center gap-2 group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#527d12] focus-visible:ring-offset-2 focus-visible:ring-offset-[#e3f79e] rounded-xl"
            >
              <span className={`text-[12px] font-medium transition-colors ${isSelected ? 'text-gray-900 font-bold' : 'text-gray-700/80 group-hover:text-gray-900'}`}>
                {dayName}
              </span>
              <span className={`w-10 h-10 rounded-full flex items-center justify-center text-[13px] font-semibold transition-all duration-200 ${isSelected ? 'bg-[#d0ed7e] border-2 border-[#82b826] text-gray-950 font-bold shadow-xs scale-105' : 'bg-white/95 text-gray-800 group-hover:bg-white shadow-2xs group-hover:scale-102'}`}>
                {date.getDate()}
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}

export default WeeklyCalendarCard;
