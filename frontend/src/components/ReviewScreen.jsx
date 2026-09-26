import React, { useState } from 'react';
import {
  CheckCircle2,
  Database,
  Plus,
  Flame,
  ArrowLeft,
  Utensils,
  Layers,
  Sparkles,
  Info
} from 'lucide-react';
import BoundingOverlay from './BoundingOverlay';
import FoodItemCard from './FoodItemCard';
import TelemetryModal from './TelemetryModal';
import { calculateMealTotals, calculateItemMacros } from '../utils/macroCalculator';
import { buildTelemetryPayload } from '../store/mealDraftStore';
import { ALL_SUPPORTED_DISHES, PORTION_UNITS_REGISTRY, GENERIC_DEFAULT_UNITS } from '../data/portionUnitsRegistry';
import { formatCalories, formatGrams, formatMg } from '../utils/formatters';

function ReviewScreen({
  draft,
  onUpdateDraftItems,
  onConfirmLogMeal,
  onBack,
  isLogging,
}) {
  const [activeItemId, setActiveItemId] = useState(draft?.items?.[0]?.item_id || null);
  const [mealType, setMealType] = useState('lunch');
  const [showTelemetryModal, setShowTelemetryModal] = useState(false);
  const [showAddDishMenu, setShowAddDishMenu] = useState(false);

  const items = draft?.items || [];
  const totals = calculateMealTotals(items);

  const handleUpdatePortion = (itemId, unitId, quantity) => {
    const updated = items.map((item) => {
      if (item.item_id !== itemId) return item;
      const unit = item.available_portion_units?.find((u) => u.unit_id === unitId) || item.selectedUnit;
      const macros = calculateItemMacros(item.nutrients_per_100g, unit?.gram_weight || 100, quantity);
      return {
        ...item,
        selectedUnitId: unitId,
        selectedUnit: unit,
        selectedQuantity: quantity,
        calculatedMacros: macros,
      };
    });
    onUpdateDraftItems(updated);
  };

  const handleUpdateLabel = (itemId, newName, newDishId, newUnits) => {
    const updated = items.map((item) => {
      if (item.item_id !== itemId) return item;
      const availableUnits = newUnits || item.available_portion_units || GENERIC_DEFAULT_UNITS;
      const selectedUnit = availableUnits[0];
      const macros = calculateItemMacros(
        item.nutrients_per_100g,
        selectedUnit.gram_weight,
        item.selectedQuantity || 1.0
      );

      return {
        ...item,
        food_name: newName,
        final_dish_id: newDishId,
        label_modified: true,
        available_portion_units: availableUnits,
        selectedUnitId: selectedUnit.unit_id,
        selectedUnit,
        calculatedMacros: macros,
      };
    });
    onUpdateDraftItems(updated);
  };

  const handleRemoveItem = (itemId) => {
    const updated = items.filter((item) => item.item_id !== itemId);
    onUpdateDraftItems(updated);
  };

  const handleAddDish = (dish) => {
    const config = PORTION_UNITS_REGISTRY[dish.id];
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
      bounding_box: [0.2, 0.2, 0.8, 0.8],
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
    onUpdateDraftItems([...items, newItem]);
    setShowAddDishMenu(false);
  };

  const handleConfirm = () => {
    const payload = buildTelemetryPayload({ ...draft, items }, mealType);
    onConfirmLogMeal(payload);
  };

  const telemetryPayload = buildTelemetryPayload({ ...draft, items }, mealType);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 animate-fade-in pb-28">
      {/* Top Bar Navigation & Actions */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <button
          type="button"
          onClick={onBack}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-500 hover:text-gray-900 bg-white border border-gray-200 px-3.5 py-2 rounded-xl hover:bg-gray-50 shadow-2xs transition-all"
        >
          <ArrowLeft className="w-4 h-4" />
          Capture Another Dish
        </button>

        <div className="flex items-center gap-2">
          {/* Meal Type Pill Selector */}
          <div className="flex items-center bg-white border border-gray-200 p-1 rounded-xl shadow-2xs">
            {['breakfast', 'lunch', 'dinner', 'snack'].map((type) => (
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
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 px-3.5 py-2 rounded-xl transition-colors"
            title="Inspect 'Log Everything' Payload"
          >
            <Database className="w-4 h-4 text-indigo-600" />
            Inspect Telemetry
          </button>
        </div>
      </div>

      {/* Screen Title */}
      <div className="mb-6">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight flex items-center gap-2">
          <span>Multi-Food Portion Review</span>
          <span className="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full">
            {items.length} dishes detected
          </span>
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          Adjust conventional portion sizes (spoons, wraps, slices) or correct dish labels. Macros recalculate in real-time.
        </p>
      </div>

      {/* Layout Grid: Visual Overlay (Left) + Portion Cards (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Meal Photo with Responsive Canvas Bounding Boxes */}
        <div className="lg:col-span-5 space-y-4 lg:sticky lg:top-8">
          <BoundingOverlay
            imageUrl={draft?.image_url}
            items={items}
            activeItemId={activeItemId}
            onSelectItem={(id) => setActiveItemId(id)}
          />

          {/* Active Learning Explainer Card */}
          <div className="bg-white border border-gray-200 rounded-2xl p-4 text-xs text-gray-600 shadow-xs flex items-start gap-3">
            <Info className="w-4 h-4 text-indigo-500 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-gray-900 block mb-0.5">Active Decision Feedback</span>
              Your unit selections and label modifications are audited with the image bounding box to improve future automated portion models for African gastronomy.
            </div>
          </div>
        </div>

        {/* Right Column: Independent Food Item Cards & Dynamic Totals */}
        <div className="lg:col-span-7 space-y-5">
          {items.map((item) => (
            <FoodItemCard
              key={item.item_id}
              item={item}
              isActive={activeItemId === item.item_id}
              onSelect={() => setActiveItemId(item.item_id)}
              onUpdatePortion={handleUpdatePortion}
              onUpdateLabel={handleUpdateLabel}
              onRemove={items.length > 1 ? handleRemoveItem : null}
            />
          ))}

          {/* Add Additional Dish Button */}
          <div className="relative">
            {showAddDishMenu ? (
              <div className="bg-white border border-gray-200 rounded-2xl p-4 shadow-lg animate-fade-in space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-gray-600">
                    Add Unrecognized African Dish
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
                Add Another Food / Side Item
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Floating Bottom Total & Decision Submission Bar */}
      <div className="fixed bottom-0 left-0 right-0 lg:right-20 bg-white/95 backdrop-blur-md border-t border-gray-200 p-4 z-30 shadow-xl">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          {/* Meal Total Macro Summary */}
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

          {/* Confirm & Log Telemetry Button */}
          <button
            type="button"
            onClick={handleConfirm}
            disabled={isLogging || items.length === 0}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-8 py-3.5 rounded-xl shadow-lg shadow-indigo-200 hover:shadow-xl transition-all active:scale-98 disabled:opacity-50 text-sm"
          >
            <CheckCircle2 className="w-4 h-4" />
            {isLogging ? 'Logging Everything & Telemetry...' : 'Confirm & Log Meal'}
          </button>
        </div>
      </div>

      {/* Telemetry Inspector Modal */}
      <TelemetryModal
        isOpen={showTelemetryModal}
        onClose={() => setShowTelemetryModal(false)}
        lastTelemetryPayload={telemetryPayload}
      />
    </div>
  );
}

export default ReviewScreen;
