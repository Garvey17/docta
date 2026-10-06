import React from 'react';
import { ArrowLeft } from 'lucide-react';

import WeeklyCalorieBarChart from './WeeklyCalorieBarChart';
import NutritionTrendsChart from './NutritionTrendsChart';

function StatisticScreen({ user, mealHistory = [], onBack }) {
  const targetCal = user?.dailyCalorieTarget || 2200;

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const today = new Date();
  const weekStart = new Date(today.getFullYear(), today.getMonth(), today.getDate() - today.getDay());
  const weekDates = Array.from({ length: 7 }, (_, index) => (
    new Date(weekStart.getFullYear(), weekStart.getMonth(), weekStart.getDate() + index)
  ));
  const dateKey = (date) => `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
  const indexByDate = new Map(weekDates.map((date, index) => [dateKey(date), index]));
  const dayTotals = Array.from({ length: 7 }, () => ({
    calories: 0,
    protein: 0,
    carbs: 0,
    fats: 0,
  }));

  mealHistory.forEach((meal) => {
    if (!meal.logged_at) return;
    const loggedDate = new Date(meal.logged_at);
    if (Number.isNaN(loggedDate.getTime())) return;
    const dayIndex = indexByDate.get(dateKey(loggedDate));
    if (dayIndex === undefined) return;
    dayTotals[dayIndex].calories += Number(meal.total_calories_kcal) || 0;
    dayTotals[dayIndex].protein += Number(meal.total_protein_g) || 0;
    dayTotals[dayIndex].carbs += Number(meal.total_carbs_g) || 0;
    dayTotals[dayIndex].fats += Number(meal.total_fat_g) || 0;
  });

  const currentDayCals = dayTotals[today.getDay()].calories;
  const weeklyData = dayNames.map((day, idx) => {
    const cals = Math.round(dayTotals[idx].calories);
    const pct = targetCal > 0 ? Math.min(100, Math.round((cals / targetCal) * 100)) : 0;
    return {
      day,
      date: weekDates[idx],
      calories: cals,
      percentage: Math.max(8, pct),
      label: `${pct}%`,
    };
  });

  const nutritionData = dayTotals.map((totals, index) => ({
    day: dayNames[index],
    protein: Math.round(totals.protein),
    carbs: Math.round(totals.carbs),
    fats: Math.round(totals.fats),
  }));

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
    </div>
  );
}




export default StatisticScreen;
