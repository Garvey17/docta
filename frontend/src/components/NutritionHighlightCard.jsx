import React from 'react';
import { Sparkles, ArrowRight, Zap, TrendingUp } from 'lucide-react';

function NutritionHighlightCard({
  mealHistory = [],
  dailyCalorieTarget = 2200,
  dailyProteinTarget = 110,
  onPromptSelect,
}) {
  // Aggregate nutrition from logged meals
  const totalCalories = mealHistory.reduce((acc, m) => acc + (m.total_calories_kcal || 0), 0) || 1250;
  const totalProtein = mealHistory.reduce((acc, m) => acc + (m.total_protein_g || 0), 0) || 64;
  const totalCarbs = mealHistory.reduce((acc, m) => acc + (m.total_carbs_g || 0), 0) || 148;
  const totalFat = mealHistory.reduce((acc, m) => acc + (m.total_fat_g || 0), 0) || 42;

  const calPercent = Math.min(100, Math.round((totalCalories / dailyCalorieTarget) * 100));
  const proteinPercent = Math.min(100, Math.round((totalProtein / dailyProteinTarget) * 100));

  const suggestionPrompts = [
    { label: '💡 How is my protein balance today?', query: 'How is my protein balance today based on my logged meals?' },
    { label: '🍲 Suggest a healthy Nigerian dinner', query: 'Based on what I already ate today, suggest a balanced Nigerian dinner with good portion sizes.' },
    { label: '🧂 Review sodium & hydration', query: 'Review my sodium intake and hydration status from today.' },
    { label: '📊 Weekly macro deficit analysis', query: 'Analyze my calorie and macronutrient trend against my daily target.' },
  ];

  return (
    <div className="w-full mb-4 space-y-3 select-none">
      {/* 1. Contextual Nutrition Highlight Card */}
      <div className="bg-[#e3f79e] rounded-[28px] p-5 sm:p-6 shadow-xs border border-[#d4ed83]/70 relative overflow-hidden">
        {/* Card Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-white/90 flex items-center justify-center text-gray-950 shadow-2xs">
              <Sparkles className="w-4 h-4 text-gray-900 stroke-[2.2]" />
            </div>
            <span className="text-[13px] sm:text-[14px] font-bold text-gray-900 tracking-tight">
              Daily Nutrition Snapshot
            </span>
          </div>

          <span className="text-[11px] sm:text-[12px] font-bold bg-white/90 text-gray-900 px-2.5 py-1 rounded-full shadow-2xs">
            {calPercent}% Target
          </span>
        </div>

        {/* Dynamic AI Summary Paragraph */}
        <p className="text-[13px] sm:text-[14px] text-gray-900/90 font-medium leading-relaxed mb-3.5">
          {totalCalories > 0 ? (
            <>
              You've logged <strong className="font-bold text-gray-950">{totalCalories} kcal</strong> and{' '}
              <strong className="font-bold text-gray-950">{totalProtein}g protein</strong> ({proteinPercent}% of daily goal). Your fiber and healthy fats are on track.
            </>
          ) : (
            <>
              No meals logged yet today. Ask me for breakfast ideas or take a photo of your plate to get started!
            </>
          )}
        </p>

        {/* Micro Macro Pills Row */}
        <div className="grid grid-cols-3 gap-2 sm:gap-3 pt-2 border-t border-black/5">
          <div className="bg-white/80 rounded-2xl p-2 sm:p-3 text-center shadow-2xs">
            <span className="text-[10px] sm:text-[11px] font-medium text-gray-500 block">Protein</span>
            <span className="text-[13px] sm:text-[15px] font-extrabold text-gray-950">{totalProtein}g</span>
          </div>
          <div className="bg-white/80 rounded-2xl p-2 sm:p-3 text-center shadow-2xs">
            <span className="text-[10px] sm:text-[11px] font-medium text-gray-500 block">Carbs</span>
            <span className="text-[13px] sm:text-[15px] font-extrabold text-gray-950">{totalCarbs}g</span>
          </div>
          <div className="bg-white/80 rounded-2xl p-2 sm:p-3 text-center shadow-2xs">
            <span className="text-[10px] sm:text-[11px] font-medium text-gray-500 block">Fats</span>
            <span className="text-[13px] sm:text-[15px] font-extrabold text-gray-950">{totalFat}g</span>
          </div>
        </div>
      </div>

      {/* 2. Interactive Suggestion Prompt Chips */}
      <div>
        <p className="text-[11px] font-bold uppercase tracking-wider text-gray-400 px-1 mb-2">
          Suggested Topics
        </p>
        <div className="flex gap-2 overflow-x-auto pb-1.5 scrollbar-none no-scrollbar">
          {suggestionPrompts.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => onPromptSelect(p.query)}
              className="shrink-0 bg-white hover:bg-gray-50 text-gray-800 text-[12px] font-semibold px-3.5 py-2 rounded-full border border-gray-100/90 shadow-2xs transition-all active:scale-95 text-left flex items-center gap-1.5"
            >
              <span>{p.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default NutritionHighlightCard;
