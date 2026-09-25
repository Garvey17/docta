import React from 'react';
import { Camera, Calendar, Sparkles, Plus, Clock, Utensils, Award, Info } from 'lucide-react';
import MacroProgressRing from './MacroProgressRing';
import MacroBar from './MacroBar';
import NutritionSummaryCards from './NutritionSummaryCards';
import MealHistoryCard from './MealHistoryCard';
import { formatCalories } from '../utils/formatters';

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
    <div className="max-w-6xl mx-auto px-4 py-8 animate-fade-in pb-20">
      {/* Top Welcome & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold text-indigo-700 bg-indigo-50 border border-indigo-100 px-3 py-0.5 rounded-full flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
              African Dietary Intelligence
            </span>
            <span className="text-xs text-gray-400 font-medium flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              Today's Log
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
            Daily Nutrition Dashboard
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Welcome back, <strong className="text-gray-800">{user?.name || 'Balkisu Habib'}</strong>. Track WAFCT African meal macros and conventional portions.
          </p>
        </div>

        {/* Quick Scan Call to Action */}
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onStartCapture}
            className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-6 py-3 rounded-2xl shadow-md shadow-indigo-100 hover:shadow-lg transition-all active:scale-95 text-sm"
          >
            <Camera className="w-4 h-4" />
            Scan African Meal
          </button>
        </div>
      </div>

      {/* Top 3 KPI Summary Cards */}
      <NutritionSummaryCards
        consumedCalories={todayTotals.calories}
        targetCalories={targetCal}
        mealsLoggedCount={mealHistory.length}
        itemsLoggedCount={mealHistory.reduce((acc, m) => acc + (m.items?.length || 0), 0)}
      />

      {/* Main Grid: Calorie Ring & Linear Macro Bars */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-10">
        {/* Calorie Ring Gauge Card */}
        <div className="lg:col-span-5 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex flex-col items-center justify-center">
          <div className="w-full flex items-center justify-between mb-4">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-500">
              Calorie Target Progress
            </span>
            <span className="text-xs font-semibold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full">
              WAFCT 2019
            </span>
          </div>

          <MacroProgressRing
            current={todayTotals.calories}
            target={targetCal}
            size={200}
            strokeWidth={16}
          />
        </div>

        {/* Linear Macro Bars Card */}
        <div className="lg:col-span-7 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex flex-col justify-between space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-gray-100">
            <div>
              <h3 className="text-base font-bold text-gray-900">
                Macronutrient Balance
              </h3>
              <p className="text-xs text-gray-500">
                Composite nutritional breakdown scaled to African conventional units
              </p>
            </div>
            <button
              type="button"
              onClick={onOpenTelemetry}
              className="text-xs text-indigo-600 hover:text-indigo-700 font-semibold"
            >
              Audit Logs
            </button>
          </div>

          <div className="space-y-4">
            <MacroBar
              label="Protein"
              current={todayTotals.protein}
              target={targetProtein}
              unit="g"
              colorClass="bg-blue-600"
              trackClass="bg-blue-50"
            />
            <MacroBar
              label="Carbohydrates"
              current={todayTotals.carbs}
              target={targetCarbs}
              unit="g"
              colorClass="bg-amber-500"
              trackClass="bg-amber-50"
            />
            <MacroBar
              label="Healthy Fats"
              current={todayTotals.fat}
              target={targetFat}
              unit="g"
              colorClass="bg-rose-500"
              trackClass="bg-rose-50"
            />
            <MacroBar
              label="Dietary Fiber"
              current={22}
              target={30}
              unit="g"
              colorClass="bg-emerald-500"
              trackClass="bg-emerald-50"
            />
            <MacroBar
              label="Sodium"
              current={1450}
              target={2300}
              unit="mg"
              colorClass="bg-indigo-600"
              trackClass="bg-indigo-50"
            />
          </div>
        </div>
      </div>

      {/* Meal History Timeline */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <Clock className="w-5 h-5 text-indigo-600" />
              Logged Meals Today
            </h3>
            <p className="text-xs text-gray-500">
              Audit trail of scanned dishes, portion units, and nutrition
            </p>
          </div>

          <button
            type="button"
            onClick={onStartCapture}
            className="inline-flex items-center gap-1.5 text-xs font-bold text-indigo-600 hover:text-indigo-700 bg-indigo-50 hover:bg-indigo-100 px-3 py-1.5 rounded-xl transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            Add Meal
          </button>
        </div>

        {mealHistory.length === 0 ? (
          <div className="bg-white border border-dashed border-gray-300 rounded-2xl p-10 text-center">
            <Utensils className="w-8 h-8 text-gray-400 mx-auto mb-3" />
            <h4 className="text-sm font-bold text-gray-800">No Meals Logged Today</h4>
            <p className="text-xs text-gray-500 mt-1 max-w-sm mx-auto">
              Scan your breakfast, lunch, or snack to automatically resolve African dishes and conventional portion sizes.
            </p>
            <button
              type="button"
              onClick={onStartCapture}
              className="mt-4 inline-flex items-center gap-2 bg-indigo-600 text-white font-semibold text-xs px-4 py-2 rounded-xl hover:bg-indigo-700 transition-colors shadow-xs"
            >
              <Camera className="w-4 h-4" />
              Scan Now
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {mealHistory.map((meal) => (
              <MealHistoryCard key={meal.meal_id} meal={meal} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default DashboardScreen;
