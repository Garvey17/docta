import React from 'react';
import { MoreVertical } from 'lucide-react';

function MealProgressCard({
  mealName = 'Breakfast',
  currentCalories = 456,
  targetCalories = 512,
  ingredients = [
    { name: 'Avocado', calories: 200, color: 'bg-[#fb7185]', trackColor: 'bg-[#ffe4e6]', progress: '75%' },
    { name: 'Bread', calories: 150, color: 'bg-[#38bdf8]', trackColor: 'bg-[#e0f2fe]', progress: '65%' },
    { name: 'Olive oil', calories: 80, color: 'bg-[#a3e635]', trackColor: 'bg-[#ecfccb]', progress: '85%' },
  ],
  onOptionsClick,
}) {
  const percentage = Math.min(100, Math.round((currentCalories / targetCalories) * 100));

  return (
    <div className="w-full bg-white rounded-[28px] p-5 sm:p-6 mb-4 shadow-xs border border-gray-100/60">
      {/* Card Header: Meal Title & More Options Button */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-[18px] font-bold text-gray-900 tracking-tight">
          {mealName}
        </h3>

        <button
          type="button"
          onClick={onOptionsClick}
          aria-label="Meal options"
          className="w-9 h-9 rounded-full bg-gray-50 hover:bg-gray-100 flex items-center justify-center text-gray-600 transition-colors active:scale-95"
        >
          <MoreVertical className="w-4 h-4 text-gray-700 stroke-[2]" />
        </button>
      </div>

      {/* Main Calorie Progress Ratio */}
      <div className="mb-3">
        <div className="text-[24px] font-extrabold text-gray-950 tracking-tight leading-none mb-3">
          {currentCalories}{' '}
          <span className="text-gray-400 font-normal text-[20px]">/</span>{' '}
          <span className="text-gray-900 font-bold">{targetCalories}</span>{' '}
          <span className="text-sm font-semibold text-gray-500 ml-0.5">kcal</span>
        </div>

        {/* Large Rounded Progress Bar with Striped Pattern Track */}
        <div className="w-full h-6 rounded-full overflow-hidden bg-striped-pattern flex p-0.5 border border-gray-100/80">
          <div
            className="h-full rounded-full bg-gradient-to-r from-[#dcfce7] via-[#bef264] to-[#84cc16] transition-all duration-700 ease-out shadow-xs"
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>

      {/* Ingredients Section Subtitle */}
      <div className="pt-2">
        <p className="text-[12px] font-medium text-gray-400 mb-3">
          {ingredients.length} ingredients
        </p>

        {/* 3 Ingredients Columns Breakdown */}
        <div className="grid grid-cols-3 gap-3">
          {ingredients.map((item, idx) => (
            <div key={`${item.name}-${idx}`} className="flex flex-col">
              <span className="text-[13px] font-bold text-gray-900 truncate mb-1.5">
                {item.name}
              </span>

              {/* Ingredient Mini Pill Bar */}
              <div className={`w-full h-2 rounded-full ${item.trackColor || 'bg-gray-100'} overflow-hidden mb-1.5`}>
                <div
                  className={`h-full rounded-full ${item.color}`}
                  style={{ width: item.progress || '70%' }}
                />
              </div>

              {/* Calories Label */}
              <div className="text-[12px] font-bold text-gray-950">
                {item.calories}{' '}
                <span className="text-[11px] font-normal text-gray-500">kcal</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default MealProgressCard;
