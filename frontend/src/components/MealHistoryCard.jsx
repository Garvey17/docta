import React from 'react';
import { Clock, Flame, ChevronRight } from 'lucide-react';
import { formatCalories, formatGrams, formatTimeAgo } from '../utils/formatters';

function MealHistoryCard({ meal }) {
  const mealTypeColors = {
    breakfast: 'bg-amber-50 text-amber-700 border-amber-200',
    lunch: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    dinner: 'bg-purple-50 text-purple-700 border-purple-200',
    snack: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  };

  const badgeColor = mealTypeColors[meal.meal_type] || mealTypeColors.lunch;

  return (
    <div className="bg-white border border-gray-200 rounded-2xl p-5 hover:border-indigo-300 hover:shadow-sm transition-all duration-200">
      <div className="flex items-center justify-between gap-3 mb-3">
        <div className="flex items-center gap-2">
          <span className={`text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full border ${badgeColor}`}>
            {meal.meal_type}
          </span>
          <span className="text-xs text-gray-400 flex items-center gap-1 font-medium">
            <Clock className="w-3 h-3" />
            {formatTimeAgo(meal.logged_at)}
          </span>
        </div>

        <div className="flex items-center gap-1 text-sm font-bold text-gray-900 bg-gray-50 px-2.5 py-1 rounded-xl">
          <Flame className="w-4 h-4 text-indigo-600" />
          <span>{formatCalories(meal.total_calories_kcal)}</span>
        </div>
      </div>

      {/* Dissected Food Items */}
      <div className="space-y-1.5 mb-3">
        {(meal.items || []).map((item, idx) => (
          <div key={idx} className="flex items-center justify-between text-xs text-gray-700">
            <div className="flex items-center gap-2 truncate">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 shrink-0" />
              <span className="font-semibold text-gray-900 truncate">{item.food_name}</span>
              <span className="text-gray-400 font-normal">
                ({item.quantity || 1} {item.unit_name || 'portion'})
              </span>
            </div>
            <span className="font-medium text-gray-500 shrink-0 ml-2">
              {formatCalories(item.calories_kcal)}
            </span>
          </div>
        ))}
      </div>

      {/* Macronutrient Pills */}
      <div className="flex items-center gap-3 pt-3 border-t border-gray-100 text-[11px] text-gray-500 font-medium">
        <span>Protein: <strong className="text-gray-800">{formatGrams(meal.total_protein_g)}</strong></span>
        <span>Carbs: <strong className="text-gray-800">{formatGrams(meal.total_carbs_g)}</strong></span>
        <span>Fat: <strong className="text-gray-800">{formatGrams(meal.total_fat_g)}</strong></span>
      </div>
    </div>
  );
}

export default MealHistoryCard;
