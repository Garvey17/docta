'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Camera, Calendar, Sparkles, Plus, Clock, Utensils } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { useDashboard } from '../hooks/useDashboard';
import { MacroProgressRing } from '../components/MacroProgressRing';
import { MacroBar } from '../components/MacroBar';
import { MealHistoryCard } from '../components/MealHistoryCard';
import NutritionSummaryCards from '../components/NutritionSummaryCards';
import RightSidebar from '../components/RightSidebar';
import Navbar from '../components/Navbar';
import TelemetryModal from '../components/TelemetryModal';
import { useMealDraftStore } from '../store/mealDraftStore';

export default function DashboardPage() {
  const { user } = useAuthStore();
  const { history, dailyTotals } = useDashboard();
  const { items } = useMealDraftStore();
  const [showTelemetry, setShowTelemetry] = useState<boolean>(false);

  const targetCal = user?.dailyCalorieTarget || 2200;
  const targetProtein = user?.dailyProteinTargetG || 110;
  const targetCarbs = user?.dailyCarbsTargetG || 250;
  const targetFat = user?.dailyFatTargetG || 65;

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-gray-900 flex flex-col">
      <RightSidebar
        currentScreen="dashboard"
        onNavigate={(screen) => {
          if (screen === 'telemetry') setShowTelemetry(true);
          else if (screen === 'capture') window.location.href = '/capture';
          else if (screen === 'review') window.location.href = '/review';
        }}
        hasActiveReview={items.length > 0}
      />

      {/* Top Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-2xs">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center text-white font-extrabold text-base shadow-sm shadow-indigo-200">
              d.
            </div>
            <div>
              <span className="font-extrabold text-gray-900 tracking-tight text-base sm:text-lg block leading-none">
                docta
              </span>
              <span className="text-[10px] font-semibold text-indigo-600 uppercase tracking-wider block mt-0.5">
                African Nutrition Intelligence
              </span>
            </div>
          </Link>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setShowTelemetry(true)}
              className="hidden sm:inline-flex items-center gap-1.5 text-xs font-semibold text-gray-600 hover:text-indigo-600 bg-gray-50 border border-gray-200 px-3 py-1.5 rounded-xl hover:bg-gray-100 transition-colors"
            >
              Active Learning Telemetry
            </button>
            <div className="inline-flex items-center gap-2 text-xs font-semibold text-gray-700 bg-white border border-gray-200 px-3.5 py-1.5 rounded-xl">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span>{user?.name || 'Balkisu Habib'}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Dashboard Screen */}
      <main className="flex-1 max-w-6xl mx-auto px-4 py-8 animate-fade-in pb-24 lg:mr-20 w-full">
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
              Welcome back, <strong className="text-gray-800">{user?.name}</strong>. Track WAFCT African meal macros and conventional portions.
            </p>
          </div>

          <Link
            href="/capture"
            className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-6 py-3 rounded-2xl shadow-md shadow-indigo-100 hover:shadow-lg transition-all active:scale-95 text-sm"
          >
            <Camera className="w-4 h-4" />
            Scan African Meal
          </Link>
        </div>

        <NutritionSummaryCards
          consumedCalories={dailyTotals.calories}
          targetCalories={targetCal}
          mealsLoggedCount={history.length}
          itemsLoggedCount={history.reduce((acc, m) => acc + (m.items?.length || 0), 0)}
        />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-10">
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
              current={dailyTotals.calories}
              target={targetCal}
              size={200}
              strokeWidth={16}
            />
          </div>

          <div className="lg:col-span-7 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex flex-col justify-between space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-gray-100">
              <div>
                <h3 className="text-base font-bold text-gray-900">
                  Macronutrient Balance
                </h3>
                <p className="text-xs text-gray-500">
                  Scaled to conventional African units (spoons, wraps, slices)
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <MacroBar label="Protein" current={dailyTotals.protein} target={targetProtein} unit="g" colorClass="bg-blue-600" trackClass="bg-blue-50" />
              <MacroBar label="Carbohydrates" current={dailyTotals.carbs} target={targetCarbs} unit="g" colorClass="bg-amber-500" trackClass="bg-amber-50" />
              <MacroBar label="Healthy Fats" current={dailyTotals.fat} target={targetFat} unit="g" colorClass="bg-rose-500" trackClass="bg-rose-50" />
              <MacroBar label="Dietary Fiber" current={22} target={30} unit="g" colorClass="bg-emerald-500" trackClass="bg-emerald-50" />
              <MacroBar label="Sodium" current={1450} target={2300} unit="mg" colorClass="bg-indigo-600" trackClass="bg-indigo-50" />
            </div>
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Clock className="w-5 h-5 text-indigo-600" />
                Logged Meals Today
              </h3>
              <p className="text-xs text-gray-500">
                Audit trail of recognized dishes and portion selections
              </p>
            </div>
            <Link
              href="/capture"
              className="inline-flex items-center gap-1.5 text-xs font-bold text-indigo-600 hover:text-indigo-700 bg-indigo-50 hover:bg-indigo-100 px-3 py-1.5 rounded-xl transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              Add Meal
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {history.map((meal) => (
              <MealHistoryCard key={meal.meal_id} meal={meal} />
            ))}
          </div>
        </div>
      </main>

      <Navbar
        currentScreen="dashboard"
        onNavigate={(screen) => {
          if (screen === 'telemetry') setShowTelemetry(true);
          else if (screen === 'capture') window.location.href = '/capture';
          else if (screen === 'review') window.location.href = '/review';
        }}
        hasActiveReview={items.length > 0}
      />

      <TelemetryModal
        isOpen={showTelemetry}
        onClose={() => setShowTelemetry(false)}
        lastTelemetryPayload={null}
      />
    </div>
  );
}
