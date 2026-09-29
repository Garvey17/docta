import React from 'react';
import { ArrowLeft, MoreVertical } from 'lucide-react';

import WeeklyCalorieBarChart from './WeeklyCalorieBarChart';
import HeartRateCard from './HeartRateCard';
import VitalsMetricCards from './VitalsMetricCards';

function StatisticScreen({ user, mealHistory = [], onBack, onOptionsClick }) {
  const targetCal = user?.dailyCalorieTarget || 2200;

  // Compute days of the week calories from real mealHistory
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const dayTotals = { 0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0 };
  let currentDayCals = 0;
  const todayDayIndex = new Date().getDay();

  mealHistory.forEach((meal) => {
    if (meal.logged_at) {
      const d = new Date(meal.logged_at);
      const dayIdx = d.getDay();
      const cals = meal.total_calories_kcal || 0;
      dayTotals[dayIdx] += cals;
      if (dayIdx === todayDayIndex) {
        currentDayCals += cals;
      }
    }
  });

  const weeklyData = dayNames.map((day, idx) => {
    const cals = Math.round(dayTotals[idx]);
    const pct = targetCal > 0 ? Math.min(100, Math.round((cals / targetCal) * 100)) : 0;
    return {
      day,
      calories: cals,
      percentage: Math.max(8, pct),
      label: `${pct}%`,
    };
  });

  return (
    <div className="max-w-md mx-auto px-4 pt-2 pb-28 animate-fade-in select-none">
      {/* 1. Top Header */}
      <header className="flex items-center justify-between pt-2 pb-5 px-1">
        {/* Back Button */}
        <button
          type="button"
          onClick={onBack}
          aria-label="Go back"
          className="w-11 h-11 bg-white hover:bg-gray-50 rounded-full flex items-center justify-center shadow-xs border border-gray-100 transition-transform active:scale-95 text-gray-800"
        >
          <ArrowLeft className="w-5 h-5 stroke-[2]" />
        </button>

        {/* Page Title */}
        <h1 className="text-[20px] sm:text-[22px] font-bold text-gray-900 tracking-tight">
          Statistic
        </h1>

        {/* Balance placeholder for centered title */}
        <div className="w-11" aria-hidden="true" />
      </header>

      {/* 2. Weekly Calorie Bar Chart Card */}
      <WeeklyCalorieBarChart
        currentCalories={Math.round(currentDayCals)}
        targetCalories={Math.round(targetCal)}
        weeklyData={weeklyData}
      />

      {/* 3. Heart Rate Card */}
      <HeartRateCard
        rate={140}
        unit="bpm"
        status="Higher than usual"
        onDetailsClick={onOptionsClick}
      />

      {/* 4. Blood Pressure & Glucose Level Cards */}
      <VitalsMetricCards
        bloodPressure={120}
        bloodPressureUnit="bpm"
        glucoseLevel={88}
        glucoseUnit="mg"
        onBpClick={onOptionsClick}
        onGlucoseClick={onOptionsClick}
      />
    </div>
  );
}




export default StatisticScreen;
