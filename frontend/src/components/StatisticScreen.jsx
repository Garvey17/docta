import React from 'react';
import { ArrowLeft } from 'lucide-react';

import WeeklyCalorieBarChart from './WeeklyCalorieBarChart';
import NutritionTrendsChart from './NutritionTrendsChart';
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

  const today = new Date();
  const weekStart = new Date(today.getFullYear(), today.getMonth(), today.getDate() - today.getDay());
  const nutritionByDate = new Map();
  mealHistory.forEach((meal) => {
    if (!meal.logged_at) return;
    const loggedDate = new Date(meal.logged_at);
    if (Number.isNaN(loggedDate.getTime())) return;
    const dateKey = `${loggedDate.getFullYear()}-${loggedDate.getMonth()}-${loggedDate.getDate()}`;
    const totals = nutritionByDate.get(dateKey) || { protein: 0, carbs: 0, fats: 0 };
    totals.protein += Number(meal.total_protein_g) || 0;
    totals.carbs += Number(meal.total_carbs_g) || 0;
    totals.fats += Number(meal.total_fat_g) || 0;
    nutritionByDate.set(dateKey, totals);
  });
  const nutritionData = Array.from({ length: 7 }, (_, index) => {
    const date = new Date(weekStart.getFullYear(), weekStart.getMonth(), weekStart.getDate() + index);
    const dateKey = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
    const totals = nutritionByDate.get(dateKey) || { protein: 0, carbs: 0, fats: 0 };
    return {
      day: dayNames[index],
      protein: Math.round(totals.protein),
      carbs: Math.round(totals.carbs),
      fats: Math.round(totals.fats),
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

      {/* 3. Weekly nutrition trends */}
      <NutritionTrendsChart data={nutritionData} />

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
