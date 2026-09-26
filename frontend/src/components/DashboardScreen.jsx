import React from 'react';
import { Camera, Calendar, Sparkles, Plus, Clock, Utensils, Award, Info } from 'lucide-react';
import MacroProgressRing from './MacroProgressRing';
import MacroBar from './MacroBar';
import NutritionSummaryCards from './NutritionSummaryCards';
import MealHistoryCard from './MealHistoryCard';
import { formatCalories } from '../utils/formatters';

import HeaderSection from './HeaderSection';
import WeeklyCalendarCard from './WeeklyCalendarCard';
import MealProgressCard from './MealProgressCard';
import ActivityMetricCards from './ActivityMetricCards';

function DashboardScreen({
  user,
  mealHistory = [],
  onStartCapture,
  onOpenTelemetry,
}) {
  // Aggregate daily totals from history
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

  const targetCal = user?.dailyCalorieTarget || 2200;
  const targetProtein = user?.dailyProteinTargetG || 110;
  const targetCarbs = user?.dailyCarbsTargetG || 250;
  const targetFat = user?.dailyFatTargetG || 65;

  return (
    <div className="max-w-md mx-auto px-4 pt-2 pb-28 animate-fade-in">
      {/* Top Greeting & Notification Header */}
      <HeaderSection
        user={user}
        onNotificationClick={onOpenTelemetry}
      />

      {/* Weekly Calendar Card */}
      <WeeklyCalendarCard />

      {/* Meal & Calorie Progress Card */}
      <MealProgressCard
        mealName="Breakfast"
        currentCalories={todayTotals.calories > 0 ? todayTotals.calories : 456}
        targetCalories={512}
        onOptionsClick={onOpenTelemetry}
      />

      {/* Activity Metric Cards (Step to walk & Drink water) */}
      <ActivityMetricCards
        steps={5234}
        waterGlasses={12}
        onStepClick={onOpenTelemetry}
        onWaterClick={onOpenTelemetry}
      />

      {/* Logged Meal History Section */}
      {mealHistory.length > 0 && (
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
          <div className="space-y-3">
            {mealHistory.slice(0, 3).map((meal) => (
              <MealHistoryCard key={meal.meal_id} meal={meal} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default DashboardScreen;


