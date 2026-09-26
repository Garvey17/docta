import React from 'react';
import { ArrowUpRight, Flame, Clock } from 'lucide-react';
import { formatCalories, formatGrams, formatTimeAgo } from '../utils/formatters';

function MealHistoryCard({ meal }) {
  const mealTypeLabels = {
    breakfast: 'Breakfast',
    lunch: 'Lunch',
    dinner: 'Dinner',
    snack: 'Snack',
  };

  const label = mealTypeLabels[meal.meal_type] || 'Meal';

  return (
    <div className="bg-white rounded-[24px] p-4 sm:p-5 shadow-xs border border-gray-100/70 hover:border-gray-200 transition-all group">
      {/* Top Header Row */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-[12px] font-bold text-gray-900 bg-[#e3f79e] px-3 py-1 rounded-full">
            {label}
          </span>
          <span className="text-[11px] text-gray-400 font-medium flex items-center gap-1">
            <Clock className="w-3 h-3 stroke-[2]" />
            {formatTimeAgo(meal.logged_at)}
          </span>
        </div>

        {/* Circular Action Button */}
        <div className="w-8 h-8 rounded-full bg-gray-50 group-hover:bg-[#e3f79e] flex items-center justify-center text-gray-700 transition-colors">
          <ArrowUpRight className="w-4 h-4 stroke-[2.2]" />
        </div>
      </div>

      {/* Calories Metric */}
      <div className="flex items-baseline gap-1.5 mb-3">
        <span className="text-[20px] sm:text-[22px] font-extrabold text-gray-950 tracking-tight">
          {meal.total_calories_kcal || 0}
        </span>
        <span className="text-[12px] font-semibold text-gray-400">
          kcal
        </span>
        <span className="text-gray-300 mx-1">•</span>
        <span className="text-[12px] font-medium text-gray-500">
          {(meal.items || []).length} items detected
        </span>
      </div>

      {/* Items Tags */}
      <div className="flex flex-wrap gap-1.5 mb-3.5">
        {(meal.items || []).map((item, idx) => {
          const colors = [
            'bg-[#ffe4e6] text-rose-700',
            'bg-[#e0f2fe] text-sky-700',
            'bg-[#ecfccb] text-lime-800',
            'bg-[#fef3c7] text-amber-800',
          ];
          const colorClass = colors[idx % colors.length];

          return (
            <span
              key={idx}
              className={`text-[11px] font-semibold px-2.5 py-1 rounded-full ${colorClass} truncate max-w-[160px]`}
            >
              {item.food_name}
            </span>
          );
        })}
      </div>

      {/* Macro Breakdown Pills */}
      <div className="grid grid-cols-3 gap-2 pt-3 border-t border-gray-100/80 text-[11px]">
        <div className="bg-gray-50/80 rounded-xl px-2.5 py-1.5 text-center">
          <span className="text-gray-400 block text-[10px] font-medium">Protein</span>
          <span className="font-bold text-gray-900">{formatGrams(meal.total_protein_g)}</span>
        </div>
        <div className="bg-gray-50/80 rounded-xl px-2.5 py-1.5 text-center">
          <span className="text-gray-400 block text-[10px] font-medium">Carbs</span>
          <span className="font-bold text-gray-900">{formatGrams(meal.total_carbs_g)}</span>
        </div>
        <div className="bg-gray-50/80 rounded-xl px-2.5 py-1.5 text-center">
          <span className="text-gray-400 block text-[10px] font-medium">Fats</span>
          <span className="font-bold text-gray-900">{formatGrams(meal.total_fat_g)}</span>
        </div>
      </div>
    </div>
  );
}

export default MealHistoryCard;
