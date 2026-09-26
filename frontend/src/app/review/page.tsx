'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  CheckCircle2,
  Database,
  Plus,
  Flame,
  ArrowLeft,
  Info
} from 'lucide-react';
import { BoundingOverlay } from '../../components/BoundingOverlay';
import { FoodItemCard } from '../../components/FoodItemCard';
import TelemetryModal from '../../components/TelemetryModal';
import { useMealDraftStore } from '../../store/mealDraftStore';
import { useLogMeal } from '../../hooks/useLogMeal';
import { useDashboard } from '../../hooks/useDashboard';
import { calculateMealTotals } from '../../utils/macroCalculator';
import { ALL_SUPPORTED_DISHES, PORTION_UNITS_REGISTRY, GENERIC_DEFAULT_UNITS } from '../../data/portionUnitsRegistry';
import { MOCK_ANALYZE_RESPONSE } from '../../lib/mockData';
import { calculateItemMacros } from '../../lib/utils';
import { formatCalories, formatGrams, formatMg } from '../../lib/utils';

export default function ReviewPage() {
  const router = useRouter();
  const {
    items,
    imageUrl,
    mealType,
    activeItemId,
    setMealType,
    setActiveItemId,
    updatePortion,
    updateLabel,
    removeItem,
    addItem,
    setDraft,
    getTelemetryPayload,
    clearDraft,
  } = useMealDraftStore();

  const { logMeal, loading: isLogging } = useLogMeal();
  const { addMealToHistory } = useDashboard();

  const [showTelemetryModal, setShowTelemetryModal] = useState<boolean>(false);
  const [showAddDishMenu, setShowAddDishMenu] = useState<boolean>(false);

  useEffect(() => {
    if (items.length === 0) {
      setDraft(MOCK_ANALYZE_RESPONSE);
    }
  }, [items.length, setDraft]);

  const totals = calculateMealTotals(items);

  const handleAddDish = (dish: { id: string; name: string }) => {
    const config = PORTION_UNITS_REGISTRY[dish.id as keyof typeof PORTION_UNITS_REGISTRY];
    const defaultUnit = config?.units?.[0] || GENERIC_DEFAULT_UNITS[0];
    const dummyMacros = {
      calories_kcal: 180.0,
      protein_g: 4.5,
      fat_g: 5.0,
      carbs_g: 28.0,
      fiber_g: 2.0,
      sodium_mg: 120.0,
      calcium_mg: 15.0,
      iron_mg: 1.2,
    };
    const newItem = {
      item_id: `manual_${Date.now()}`,
      food_name: dish.name,
      display_name: dish.name,
      predicted_dish_id: dish.id,
      final_dish_id: dish.id,
      label_modified: false,
      confidence: 1.0,
      bounding_box: [0.2, 0.2, 0.8, 0.8] as [number, number, number, number],
      default_unit_id: defaultUnit.unit_id,
      default_quantity: 1.0,
      default_weight_g: defaultUnit.gram_weight,
      available_portion_units: config?.units || GENERIC_DEFAULT_UNITS,
      selectedUnitId: defaultUnit.unit_id,
      selectedUnit: defaultUnit,
      selectedQuantity: 1.0,
      nutrients_per_100g: dummyMacros,
      calculatedMacros: calculateItemMacros(dummyMacros, defaultUnit.gram_weight, 1.0),
    };
    addItem(newItem);
    setShowAddDishMenu(false);
  };

  const handleConfirm = async () => {
    const payload = getTelemetryPayload();
    const result = await logMeal(payload);

    addMealToHistory({
      meal_id: result.meal_id || `meal_${Date.now()}`,
      meal_type: mealType,
      logged_at: payload.logged_at,
      total_calories_kcal: totals.totalCaloriesKcal,
      total_protein_g: totals.totalProteinG,
      total_carbs_g: totals.totalCarbsG,
      total_fat_g: totals.totalFatG,
      items: payload.items.map((i) => ({
        food_name: i.foodName,
        unit_name: i.selectedUnitId,
        quantity: i.selectedQuantity,
        gram_weight: i.gramWeight,
        calories_kcal: i.caloriesKcal,
      })),
    });

    clearDraft();
    router.push('/');
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-gray-900 pb-28">
      {/* Top Bar */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-2xs">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link
            href="/capture"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-500 hover:text-gray-900 bg-white border border-gray-200 px-3.5 py-1.5 rounded-xl hover:bg-gray-50 transition-all shadow-2xs"
          >
            <ArrowLeft className="w-4 h-4" />
            Capture Another Dish
          </Link>

          <div className="flex items-center gap-2">
            <div className="flex items-center bg-gray-50 border border-gray-200 p-1 rounded-xl">
              {(['breakfast', 'lunch', 'dinner', 'snack'] as const).map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setMealType(type)}
                  className={`px-3 py-1 rounded-lg text-xs font-bold capitalize transition-colors ${
                    mealType === type
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'text-gray-500 hover:text-gray-900'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>

            <button
              type="button"
              onClick={() => setShowTelemetryModal(true)}
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 px-3.5 py-1.5 rounded-xl transition-colors"
            >
              <Database className="w-4 h-4 text-indigo-600" />
              Telemetry
            </button>
          </div>
        </div>
      </header>

      {/* Main Review Section */}
      <main className="max-w-6xl mx-auto px-4 py-8 animate-fade-in">
        <div className="mb-6">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight flex items-center gap-2">
            <span>Multi-Food Portion Review</span>
            <span className="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full">
              {items.length} detected
            </span>
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Choose culturally standard portion units (spoons, wraps, slices) or modify dish labels.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          <div className="lg:col-span-5 space-y-4 lg:sticky lg:top-20">
            <BoundingOverlay
              imageUrl={imageUrl || undefined}
              items={items}
              activeItemId={activeItemId}
              onSelectItem={(id) => setActiveItemId(id)}
            />

            <div className="bg-white border border-gray-200 rounded-2xl p-4 text-xs text-gray-600 shadow-xs flex items-start gap-3">
              <Info className="w-4 h-4 text-indigo-500 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-gray-900 block mb-0.5">Decision Telemetry Active</span>
                Every portion choice and label modification is persistently logged to train future portion size AI models for African diets.
              </div>
            </div>
          </div>

          <div className="lg:col-span-7 space-y-5">
            {items.map((item) => (
              <FoodItemCard
                key={item.item_id}
                item={item}
                isActive={activeItemId === item.item_id}
                onSelect={() => setActiveItemId(item.item_id)}
                onUpdatePortion={updatePortion}
                onUpdateLabel={updateLabel}
                onRemove={items.length > 1 ? removeItem : null}
              />
            ))}

            <div className="relative">
              {showAddDishMenu ? (
                <div className="bg-white border border-gray-200 rounded-2xl p-4 shadow-lg animate-fade-in space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase tracking-wider text-gray-600">
                      Add African Dish
                    </span>
                    <button
                      type="button"
                      onClick={() => setShowAddDishMenu(false)}
                      className="text-xs text-gray-400 hover:text-gray-600 font-semibold"
                    >
                      Cancel
                    </button>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                    {ALL_SUPPORTED_DISHES.map((d) => (
                      <button
                        key={d.id}
                        type="button"
                        onClick={() => handleAddDish(d)}
                        className="text-left p-2.5 rounded-xl border border-gray-200 hover:border-indigo-400 hover:bg-indigo-50/50 text-xs font-semibold text-gray-800 transition-colors"
                      >
                        {d.name}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => setShowAddDishMenu(true)}
                  className="w-full py-3.5 border-2 border-dashed border-gray-300 hover:border-indigo-400 rounded-2xl text-xs font-bold text-gray-600 hover:text-indigo-600 flex items-center justify-center gap-2 transition-colors bg-white/50"
                >
                  <Plus className="w-4 h-4" />
                  Add Another Dish
                </button>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Floating Bottom Total Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-md border-t border-gray-200 p-4 z-30 shadow-xl">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4 sm:gap-6 text-center sm:text-left">
            <div>
              <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider block">
                Total Calories
              </span>
              <span className="text-2xl font-extrabold text-indigo-700 tracking-tight flex items-center gap-1 justify-center sm:justify-start">
                <Flame className="w-5 h-5 fill-indigo-600 text-indigo-600" />
                {formatCalories(totals.totalCaloriesKcal)}
              </span>
            </div>

            <div className="hidden sm:flex items-center gap-4 text-xs font-semibold text-gray-600 border-l border-gray-200 pl-6">
              <div>
                <span className="text-gray-400 block text-[10px] uppercase">Protein</span>
                <span className="text-gray-900 font-bold">{formatGrams(totals.totalProteinG)}</span>
              </div>
              <div>
                <span className="text-gray-400 block text-[10px] uppercase">Carbs</span>
                <span className="text-gray-900 font-bold">{formatGrams(totals.totalCarbsG)}</span>
              </div>
              <div>
                <span className="text-gray-400 block text-[10px] uppercase">Fat</span>
                <span className="text-gray-900 font-bold">{formatGrams(totals.totalFatG)}</span>
              </div>
              <div>
                <span className="text-gray-400 block text-[10px] uppercase">Sodium</span>
                <span className="text-gray-900 font-bold">{formatMg(totals.totalSodiumMg)}</span>
              </div>
            </div>
          </div>

          <button
            type="button"
            onClick={handleConfirm}
            disabled={isLogging || items.length === 0}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-8 py-3.5 rounded-xl shadow-lg shadow-indigo-200 hover:shadow-xl transition-all active:scale-98 disabled:opacity-50 text-sm"
          >
            <CheckCircle2 className="w-4 h-4" />
            {isLogging ? 'Logging Telemetry...' : 'Confirm & Log Meal'}
          </button>
        </div>
      </div>

      <TelemetryModal
        isOpen={showTelemetryModal}
        onClose={() => setShowTelemetryModal(false)}
        lastTelemetryPayload={getTelemetryPayload()}
      />
    </div>
  );
}
