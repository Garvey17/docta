import React from 'react';
import HeaderSection from './HeaderSection';
import WeeklyCalendarCard from './WeeklyCalendarCard';
import MealProgressCard from './MealProgressCard';
import ActivityMetricCards from './ActivityMetricCards';
import MealHistoryCard from './MealHistoryCard';

function DashboardScreen({
  user,
  mealHistory = [],
  dashboardData = null,
  onStartCapture,
  onOpenTelemetry,
  onLogout,
}) {
  // Aggregate daily totals from real history
  const todayTotals = mealHistory.reduce(
    (acc, m) => {
      acc.calories += m.total_calories_kcal || 0;
      acc.protein += m.total_protein_g || 0;
      acc.carbs += m.total_carbs_g || 0;
      acc.fat += m.total_fat_g || 0;
      return acc;
    },
    { calories: 0, protein: 0, carbs: 0, fat: 0 }
  );

  const todayCalories = dashboardData?.today_summary?.total_calories_kcal ?? todayTotals.calories;
  const targetCal = dashboardData?.targets?.target_calories_kcal ?? user?.dailyCalorieTarget ?? 2200;
  const targetProtein = dashboardData?.targets?.target_protein_g ?? user?.dailyProteinTargetG ?? 110;
  const targetCarbs = dashboardData?.targets?.target_carbs_g ?? user?.dailyCarbsTargetG ?? 250;
  const targetFat = dashboardData?.targets?.target_fat_g ?? user?.dailyFatTargetG ?? 65;

  return (
    <div className="max-w-md mx-auto px-4 pt-2 pb-28 animate-fade-in">
      {/* Top Greeting & Notification Header */}
      <HeaderSection
        user={user}
        onLogout={onLogout}
      />

      {/* Weekly Calendar Card */}
      <WeeklyCalendarCard />

      {/* Meal & Calorie Progress Card */}
      <MealProgressCard
        mealName={mealHistory[0]?.meal_type ? (mealHistory[0].meal_type.charAt(0).toUpperCase() + mealHistory[0].meal_type.slice(1)) : "Today's Intake"}
        currentCalories={Math.round(todayCalories)}
        targetCalories={Math.round(targetCal)}
        ingredients={
          mealHistory[0]?.items?.length > 0
            ? mealHistory[0].items.slice(0, 3).map((item, idx) => ({
                name: item.food_name || 'Dish',
                calories: Math.round(item.calories_kcal || 0),
                color: idx === 0 ? 'bg-[#fb7185]' : idx === 1 ? 'bg-[#38bdf8]' : 'bg-[#a3e635]',
                trackColor: idx === 0 ? 'bg-[#ffe4e6]' : idx === 1 ? 'bg-[#e0f2fe]' : 'bg-[#ecfccb]',
                progress: `${Math.min(100, Math.round(((item.calories_kcal || 0) / Math.max(1, todayCalories)) * 100))}%`,
              }))
            : [
                { name: 'Protein', calories: Math.round(todayTotals.protein * 4), color: 'bg-[#fb7185]', trackColor: 'bg-[#ffe4e6]', progress: `${Math.min(100, Math.round((todayTotals.protein / targetProtein) * 100))}%` },
                { name: 'Carbs', calories: Math.round(todayTotals.carbs * 4), color: 'bg-[#38bdf8]', trackColor: 'bg-[#e0f2fe]', progress: `${Math.min(100, Math.round((todayTotals.carbs / targetCarbs) * 100))}%` },
                { name: 'Fat', calories: Math.round(todayTotals.fat * 9), color: 'bg-[#a3e635]', trackColor: 'bg-[#ecfccb]', progress: `${Math.min(100, Math.round((todayTotals.fat / targetFat) * 100))}%` },
              ]
        }
        onOptionsClick={onOpenTelemetry}
      />

      {/* Activity Metric Cards (mock streak & water reminder) */}
      <ActivityMetricCards
        streakDays={4}
        waterGlasses={12}
        onWaterClick={onOpenTelemetry}
      />

      {/* Logged Meal History Section */}
      <div className="mt-5 pt-1">
        <div className="flex items-center justify-between mb-3 px-1">
          <h4 className="text-[16px] font-bold text-gray-900 tracking-tight">
            Recent Scans
          </h4>
          <button
            type="button"
            onClick={onStartCapture}
            className="text-[12px] font-bold text-gray-900 bg-[#e3f79e] hover:bg-[#d5ee8c] px-3 py-1.5 rounded-full transition-transform active:scale-95 shadow-2xs"
          >
            + Scan meal
          </button>
        </div>

        {mealHistory.length > 0 ? (
          <div className="space-y-3">
            {mealHistory.slice(0, 5).map((meal) => (
              <MealHistoryCard key={meal.meal_id} meal={meal} />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-3xl p-6 text-center border border-gray-100 shadow-xs">
            <p className="text-sm font-semibold text-gray-700 mb-1">No meals logged yet today</p>
            <p className="text-xs text-gray-400 mb-4">Snap a photo of your African dish to log nutrition</p>
            <button
              type="button"
              onClick={onStartCapture}
              className="inline-flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-4 py-2 rounded-xl transition-all shadow-xs"
            >
              Scan First Meal
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default DashboardScreen;


