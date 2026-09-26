import React from 'react';
import { Minus, Plus, Scale } from 'lucide-react';
import { formatGrams } from '../utils/formatters';

function PortionUnitSelector({
  availableUnits = [],
  selectedUnitId,
  selectedQuantity = 1.0,
  onUnitChange,
  onQuantityChange,
}) {
  const currentUnit = availableUnits.find((u) => u.unit_id === selectedUnitId) || availableUnits[0];
  const step = 0.5;
  const minQty = 0.5;
  const maxQty = 10.0;

  const handleDecrement = () => {
    const next = Math.max(minQty, Math.round((selectedQuantity - step) * 10) / 10);
    onQuantityChange(next);
  };

  const handleIncrement = () => {
    const next = Math.min(maxQty, Math.round((selectedQuantity + step) * 10) / 10);
    onQuantityChange(next);
  };

  const totalItemGrams = Math.round((currentUnit?.gram_weight || 100) * selectedQuantity);

  return (
    <div className="space-y-3">
      {/* Unit Selector Dropdown */}
      <div>
        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5 flex items-center justify-between">
          <span>Conventional Unit</span>
          <span className="text-indigo-600 font-medium normal-case flex items-center gap-1">
            <Scale className="w-3 h-3" />
            Total: {formatGrams(totalItemGrams)}
          </span>
        </label>
        <select
          value={selectedUnitId || currentUnit?.unit_id}
          onChange={(e) => onUnitChange(e.target.value)}
          className="w-full bg-white border border-gray-200 text-gray-800 text-sm rounded-xl px-3.5 py-2.5 font-medium shadow-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition-all cursor-pointer"
        >
          {availableUnits.map((u) => (
            <option key={u.unit_id} value={u.unit_id}>
              {u.unit_name} ({u.gram_weight}g) {u.description ? `— ${u.description}` : ''}
            </option>
          ))}
        </select>
      </div>

      {/* Quantity Stepper */}
      <div>
        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5">
          Quantity / Servings
        </label>
        <div className="flex items-center gap-3">
          <div className="flex items-center border border-gray-200 rounded-xl bg-gray-50 p-1 shadow-2xs">
            <button
              type="button"
              onClick={handleDecrement}
              disabled={selectedQuantity <= minQty}
              className="w-9 h-9 rounded-lg bg-white border border-gray-200 flex items-center justify-center text-gray-700 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-2xs active:scale-95"
              aria-label="Decrease quantity"
            >
              <Minus className="w-4 h-4" />
            </button>

            <span className="w-16 text-center text-sm font-bold text-gray-900 select-none">
              {selectedQuantity.toFixed(1)}
            </span>

            <button
              type="button"
              onClick={handleIncrement}
              disabled={selectedQuantity >= maxQty}
              className="w-9 h-9 rounded-lg bg-white border border-gray-200 flex items-center justify-center text-gray-700 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-2xs active:scale-95"
              aria-label="Increase quantity"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>

          <span className="text-xs text-gray-500 font-medium">
            {selectedQuantity === 1 ? 'serving' : 'servings'} of {currentUnit?.unit_name || 'unit'}
          </span>
        </div>
      </div>
    </div>
  );
}

export default PortionUnitSelector;
