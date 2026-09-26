import React from 'react';
import { ArrowLeft, MoreVertical } from 'lucide-react';

import WeeklyCalorieBarChart from './WeeklyCalorieBarChart';
import HeartRateCard from './HeartRateCard';
import VitalsMetricCards from './VitalsMetricCards';

function StatisticScreen({ onBack, onOptionsClick }) {
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

        {/* Options Button */}
        <button
          type="button"
          onClick={onOptionsClick}
          aria-label="More options"
          className="w-11 h-11 bg-white hover:bg-gray-50 rounded-full flex items-center justify-center shadow-xs border border-gray-100 transition-transform active:scale-95 text-gray-800"
        >
          <MoreVertical className="w-5 h-5 stroke-[2]" />
        </button>
      </header>

      {/* 2. Weekly Calorie Bar Chart Card */}
      <WeeklyCalorieBarChart
        currentCalories={1250}
        targetCalories={1920}
      />

      {/* 3. Heart Rate Card */}
      <HeartRateCard
        rate={140}
        unit="bpm"
        status="Higher than usual"
        onDetailsClick={onOptionsClick}
      />

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
