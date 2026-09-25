import React, { useState } from 'react';
import { Edit3, Check, Trash2, Flame, AlertCircle } from 'lucide-react';
import PortionUnitSelector from './PortionUnitSelector';
import { ALL_SUPPORTED_DISHES, PORTION_UNITS_REGISTRY } from '../data/portionUnitsRegistry';
import { formatCalories, formatGrams, formatMg, formatConfidence } from '../utils/formatters';

function FoodItemCard({
  item,
  isActive,
  onSelect,
  onUpdatePortion,
  onUpdateLabel,
  onRemove,
}) {
  const [isEditingLabel, setIsEditingLabel] = useState(false);
  const [selectedDishId, setSelectedDishId] = useState(item.final_dish_id || item.predicted_dish_id);

  const macros = item.calculatedMacros || {
    gramWeight: 0,
    caloriesKcal: 0,
    proteinG: 0,
    fatG: 0,
    carbsG: 0,
    fiberG: 0,
    sodiumMg: 0,
  };

  const handleSaveLabelCorrection = () => {
    const chosen = ALL_SUPPORTED_DISHES.find((d) => d.id === selectedDishId);
    if (chosen) {
      const unitsConfig = PORTION_UNITS_REGISTRY[chosen.id];
      onUpdateLabel(item.item_id, chosen.name, chosen.id, unitsConfig?.units);
    }
    setIsEditingLabel(false);
  };

  return (
    <div
      onClick={onSelect}
      className={`bg-white border rounded-2xl p-5 transition-all duration-200 shadow-sm ${
        isActive
          ? 'border-indigo-500 ring-2 ring-indigo-500/10 shadow-md'
          : 'border-gray-200 hover:border-gray-300'
      }`}
    >
      {/* Header: Label & Confidence */}
      <div className="flex items-start justify-between gap-3 mb-4">
        <div className="flex-1 min-w-0">
          {isEditingLabel ? (
            <div className="flex items-center gap-2">
              <select
                value={selectedDishId}
                onChange={(e) => setSelectedDishId(e.target.value)}
                className="bg-white border border-indigo-300 text-gray-900 text-sm rounded-xl px-3 py-1.5 font-semibold focus:ring-2 focus:ring-indigo-500/30"
              >
                {ALL_SUPPORTED_DISHES.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={handleSaveLabelCorrection}
                className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center hover:bg-indigo-700 transition-colors shadow-xs"
                title="Save label correction"
              >
                <Check className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className="text-base font-bold text-gray-900 truncate">
                {item.food_name || item.display_name}
              </h4>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsEditingLabel(true);
                }}
                className="text-gray-400 hover:text-indigo-600 p-1 rounded-md transition-colors"
                title="Correct Dish Name"
              >
                <Edit3 className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* Subtitle / Flags */}
          <div className="flex items-center gap-2 mt-1">
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200/80 px-2 py-0.5 rounded-full">
              {formatConfidence(item.confidence || 0.92)}
            </span>

            {item.label_modified && (
              <span className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
                <AlertCircle className="w-3 h-3" />
                Corrected by User
              </span>
            )}
          </div>
        </div>

        {onRemove && (
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onRemove(item.item_id);
            }}
            className="text-gray-400 hover:text-rose-600 p-1.5 rounded-lg hover:bg-rose-50 transition-colors"
            title="Remove item"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Conventional Portion Selector */}
      <PortionUnitSelector
        availableUnits={item.available_portion_units || []}
        selectedUnitId={item.selectedUnitId}
        selectedQuantity={item.selectedQuantity}
        onUnitChange={(unitId) => onUpdatePortion(item.item_id, unitId, item.selectedQuantity)}
        onQuantityChange={(qty) => onUpdatePortion(item.item_id, item.selectedUnitId, qty)}
      />

      {/* Real-time Subtotal Nutrition Pill Bar */}
      <div className="mt-4 pt-3 border-t border-gray-100 flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex items-center gap-1.5 font-bold text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-lg">
          <Flame className="w-3.5 h-3.5" />
          <span>{formatCalories(macros.caloriesKcal)}</span>
        </div>

        <div className="flex items-center gap-3 text-gray-500 font-medium">
          <span>P: <strong className="text-gray-800">{formatGrams(macros.proteinG)}</strong></span>
          <span>C: <strong className="text-gray-800">{formatGrams(macros.carbsG)}</strong></span>
          <span>F: <strong className="text-gray-800">{formatGrams(macros.fatG)}</strong></span>
          <span>Na: <strong className="text-gray-800">{formatMg(macros.sodiumMg)}</strong></span>
        </div>
      </div>
    </div>
  );
}

export default FoodItemCard;
