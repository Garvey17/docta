import React from 'react';
import { Flame, Utensils, CheckCircle2, TrendingUp } from 'lucide-react';
import { SUMMARY_CARD_COLOR_CLASSES } from '../utils/scoreColors';
import { formatCalories } from '../utils/formatters';

function NutritionSummaryCards({
  consumedCalories = 1380,
  targetCalories = 2200,
  mealsLoggedCount = 2,
  itemsLoggedCount = 4,
}) {
  const caloriePct = Math.round((consumedCalories / targetCalories) * 100);
  const remaining = Math.max(0, targetCalories - consumedCalories);

  const calorieColor = caloriePct > 105
    ? SUMMARY_CARD_COLOR_CLASSES.red
    : caloriePct >= 80
    ? SUMMARY_CARD_COLOR_CLASSES.amber
    : SUMMARY_CARD_COLOR_CLASSES.indigo;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
      {/* Overall Calorie Budget Card */}
      <div className={`p-6 rounded-2xl border-2 ${calorieColor} transition-all duration-300 hover:shadow-md hover:scale-[1.01] cursor-pointer`}>
        <div className="flex items-center justify-between mb-2">
          <Flame className="w-6 h-6 text-indigo-600" />
          <span className="text-xs font-semibold uppercase tracking-wider opacity-75">Daily Budget</span>
        </div>
        <div className="text-3xl font-extrabold mb-1 tracking-tight">
          {formatCalories(consumedCalories)}
        </div>
        <div className="text-xs opacity-80 font-medium">
          {caloriePct}% of {formatCalories(targetCalories)} target ({remaining} kcal left)
        </div>
      </div>

      {/* Logged Meals Counter Card */}
      <div className={`p-6 rounded-2xl border-2 ${SUMMARY_CARD_COLOR_CLASSES.green} transition-all duration-300 hover:shadow-md hover:scale-[1.01] cursor-pointer`}>
        <div className="flex items-center justify-between mb-2">
          <Utensils className="w-6 h-6 text-emerald-600" />
          <span className="text-xs font-semibold uppercase tracking-wider opacity-75">Meals Tracked</span>
        </div>
        <div className="text-3xl font-extrabold mb-1 tracking-tight">
          {mealsLoggedCount} <span className="text-base font-semibold text-emerald-700">meals</span>
        </div>
        <div className="text-xs opacity-80 font-medium">
          {itemsLoggedCount} recognized African dishes
        </div>
      </div>

      {/* Decision Telemetry Status Card */}
      <div className={`p-6 rounded-2xl border-2 ${SUMMARY_CARD_COLOR_CLASSES.purple} transition-all duration-300 hover:shadow-md hover:scale-[1.01] cursor-pointer`}>
        <div className="flex items-center justify-between mb-2">
          <CheckCircle2 className="w-6 h-6 text-purple-600" />
          <span className="text-xs font-semibold uppercase tracking-wider opacity-75">Active Learning</span>
        </div>
        <div className="text-3xl font-extrabold mb-1 tracking-tight">
          100%
        </div>
        <div className="text-xs opacity-80 font-medium">
          Conventional portion & label telemetry active
        </div>
      </div>
    </div>
  );
}

export default NutritionSummaryCards;
