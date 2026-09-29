import React, { useState } from 'react';
import {
  CheckCircle2,
  Database,
  Plus,
  Flame,
  ArrowLeft,
  MoreVertical,
  Info
} from 'lucide-react';
import BoundingOverlay from './BoundingOverlay';
import FoodItemCard from './FoodItemCard';
import TelemetryModal from './TelemetryModal';
import { calculateMealTotals, calculateItemMacros } from '../utils/macroCalculator';
import { buildTelemetryPayload } from '../store/mealDraftStore';
import { ALL_SUPPORTED_DISHES, PORTION_UNITS_REGISTRY, GENERIC_DEFAULT_UNITS } from '../data/portionUnitsRegistry';
import { formatCalories, formatGrams, formatMg } from '../utils/formatters';
import { fetchDishDetails } from '../api/mealApi';

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

  const handleUpdatePortion = (itemId, unitId, quantity, customGrams = null) => {
    const updated = items.map((item) => {
      if (item.item_id !== itemId) return item;
      let unit = item.available_portion_units?.find((u) => u.unit_id === unitId);
      if (unitId === 'custom_grams') {
        const grams = customGrams !== null && customGrams !== undefined ? customGrams : (item.selectedUnit?.gram_weight || 150.0);
        unit = {
          unit_id: 'custom_grams',
          unit_name: 'Custom Grams',
          gram_weight: grams,
          description: 'Custom gram mass',
        };
      } else if (!unit) {
        unit = item.selectedUnit;
      }
      const effectiveQty = unitId === 'custom_grams' ? 1.0 : quantity;
      const macros = calculateItemMacros(item.nutrients_per_100g, unit?.gram_weight || 100, effectiveQty);
      return {
        ...item,
        selectedUnitId: unitId,
        selectedUnit: unit,
        selectedQuantity: effectiveQty,
        calculatedMacros: macros,
      };
    });
    onUpdateDraftItems(updated);
  };

  const handleUpdateLabel = async (itemId, newName, newDishId, newUnits) => {
    let freshNutrients = null;
    let freshUnits = newUnits;
    let freshDisplayName = newName;

    try {
      const details = await fetchDishDetails(newDishId);
      if (details) {
        freshNutrients = details.nutrients_per_100g;
        freshUnits = details.available_portion_units || newUnits;
        freshDisplayName = details.display_name || newName;
      }
    } catch (e) {
      console.warn('Failed to fetch real dish details for correction:', e);
    }

    const updated = items.map((item) => {
      if (item.item_id !== itemId) return item;
      const availableUnits = freshUnits || item.available_portion_units || GENERIC_DEFAULT_UNITS;
      const selectedUnit = availableUnits[0];
      const nutrients100g = freshNutrients || item.nutrients_per_100g;
      const macros = calculateItemMacros(
        nutrients100g,
        selectedUnit.gram_weight,
        item.selectedQuantity || 1.0
      );

      return {
        ...item,
        food_name: freshDisplayName,
        display_name: freshDisplayName,
        final_dish_id: newDishId,
        label_modified: true,
        available_portion_units: availableUnits,
        selectedUnitId: selectedUnit.unit_id,
        selectedUnit,
        nutrients_per_100g: nutrients100g,
        calculatedMacros: macros,
      };
    });
    onUpdateDraftItems(updated);
  };

  const handleRemoveItem = (itemId) => {
    const updated = items.filter((item) => item.item_id !== itemId);
    onUpdateDraftItems(updated);
  };

  const handleAddDish = async (dish) => {
    let details = null;
    try {
      details = await fetchDishDetails(dish.id);
    } catch (e) {
      console.warn('Failed to fetch dish details for added dish:', e);
    }

    const config = PORTION_UNITS_REGISTRY[dish.id];
    const availableUnits = details?.available_portion_units?.length > 0
      ? details.available_portion_units
      : config?.units || GENERIC_DEFAULT_UNITS;

    const defaultUnitId = details?.default_unit_id || availableUnits[0].unit_id;
    const defaultUnit = availableUnits.find((u) => u.unit_id === defaultUnitId) || availableUnits[0];
    const defaultQty = details?.default_quantity || 1.0;
    const nutrients100g = details?.nutrients_per_100g || {
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
      food_name: details?.display_name || dish.name,
      display_name: details?.display_name || dish.name,
      predicted_dish_id: details?.dish_id || dish.id,
      final_dish_id: details?.dish_id || dish.id,
      label_modified: false,
      confidence: 1.0,
      bounding_box: [0.2, 0.2, 0.8, 0.8],
      default_unit_id: defaultUnit.unit_id,
      default_quantity: defaultQty,
      default_weight_g: defaultUnit.gram_weight * defaultQty,
      available_portion_units: availableUnits,
      selectedUnitId: defaultUnit.unit_id,
      selectedUnit: defaultUnit,
      selectedQuantity: defaultQty,
      nutrients_per_100g: nutrients100g,
      calculatedMacros: calculateItemMacros(nutrients100g, defaultUnit.gram_weight, defaultQty),
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
    <div className="max-w-md mx-auto px-4 pt-2 pb-36 animate-fade-in select-none">
      {/* 1. Top Header */}
      <header className="flex items-center justify-between pt-2 pb-4 px-1">
        <button
          type="button"
          onClick={onBack}
          aria-label="Go back"
          className="w-11 h-11 bg-white hover:bg-gray-50 rounded-full flex items-center justify-center shadow-xs border border-gray-100 transition-transform active:scale-95 text-gray-800"
        >
          <ArrowLeft className="w-5 h-5 stroke-[2]" />
        </button>

        <h1 className="text-[20px] sm:text-[22px] font-bold text-gray-900 tracking-tight">
          Review Meal
        </h1>

        <button
          type="button"
          onClick={() => setShowTelemetryModal(true)}
          aria-label="Inspect Telemetry"
          className="w-11 h-11 bg-white hover:bg-gray-50 rounded-full flex items-center justify-center shadow-xs border border-gray-100 transition-transform active:scale-95 text-gray-800"
        >
          <MoreVertical className="w-5 h-5 stroke-[2]" />
        </button>
      </header>

      {/* 2. Meal Category Pill Selector */}
      <div className="flex items-center justify-center gap-1.5 mb-4 bg-white p-1.5 rounded-full shadow-xs border border-gray-100">
        {['breakfast', 'lunch', 'dinner', 'snack'].map((type) => (
          <button
            key={type}
            type="button"
            onClick={() => setMealType(type)}
            className={`flex-1 py-1.5 rounded-full text-xs font-bold capitalize transition-all ${
              mealType === type
                ? 'bg-[#e3f79e] text-gray-950 shadow-2xs'
                : 'text-gray-500 hover:text-gray-900'
            }`}
          >
            {type}
          </button>
        ))}
      </div>

      {/* 3. Image Overlay */}
      <div className="mb-4">
        <BoundingOverlay
          imageUrl={draft?.image_url}
          items={items}
          activeItemId={activeItemId}
          onSelectItem={(id) => setActiveItemId(id)}
        />
      </div>

      {/* 4. Food Items Cards */}
      <div className="space-y-3.5 mb-4">
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

        {/* Add Side Dish Button */}
        <div>
          {showAddDishMenu ? (
            <div className="bg-white rounded-[24px] p-4 shadow-sm border border-gray-100 space-y-3 animate-fade-in">
              <div className="flex items-center justify-between px-1">
                <span className="text-xs font-bold text-gray-800">
                  Select African Dish
                </span>
                <button
                  type="button"
                  onClick={() => setShowAddDishMenu(false)}
                  className="text-xs text-gray-400 hover:text-gray-600 font-semibold"
                >
                  Cancel
                </button>
              </div>
              <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto">
                {ALL_SUPPORTED_DISHES.map((d) => (
                  <button
                    key={d.id}
                    type="button"
                    onClick={() => handleAddDish(d)}
                    className="text-left p-2.5 rounded-xl border border-gray-100 hover:border-lime-400 hover:bg-[#e3f79e]/20 text-xs font-semibold text-gray-800 transition-colors"
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
              className="w-full py-3 border-2 border-dashed border-gray-200 hover:border-gray-300 rounded-[20px] text-xs font-bold text-gray-600 flex items-center justify-center gap-1.5 transition-colors bg-white/60"
            >
              <Plus className="w-4 h-4" />
              Add Another Dish
            </button>
          )}
        </div>
      </div>

      {/* 5. Fixed Floating Submission Pill Bar */}
      <div className="fixed bottom-4 left-0 right-0 z-40 flex justify-center px-4 pointer-events-none">
        <div className="pointer-events-auto bg-white/95 backdrop-blur-md rounded-full px-5 py-3 shadow-2xl shadow-black/15 border border-gray-100 flex items-center justify-between w-full max-w-[390px] gap-3">
          <div className="flex items-baseline gap-1">
            <Flame className="w-4 h-4 fill-gray-950 text-gray-950" />
            <span className="text-[18px] font-extrabold text-gray-950 tracking-tight">
              {formatCalories(totals.totalCaloriesKcal)}
            </span>
            <span className="text-[11px] font-semibold text-gray-400">kcal</span>
          </div>

          <button
            type="button"
            onClick={handleConfirm}
            disabled={isLogging || items.length === 0}
            className="inline-flex items-center gap-2 bg-gray-950 hover:bg-black text-white font-bold px-6 py-2.5 rounded-full shadow-md active:scale-95 transition-all text-xs"
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-[#bef264]" />
            {isLogging ? 'Logging...' : 'Confirm Meal'}
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
