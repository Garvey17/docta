import { calculateItemMacros } from '../utils/macroCalculator.js';

/**
 * Normalizes detected items by assigning default units and precomputing macros.
 */
export function initializeDraftItems(detectedItems = []) {
  return detectedItems.map((item) => {
    const selectedUnitId = item.default_unit_id || item.available_portion_units?.[0]?.unit_id || 'standard_serving';
    const selectedUnit = item.available_portion_units?.find((u) => u.unit_id === selectedUnitId) ||
      item.available_portion_units?.[0] || {
        unit_id: selectedUnitId,
        unit_name: 'Standard Portion',
        gram_weight: item.default_weight_g || 150.0,
        description: 'Standard portion'
      };

    const selectedQuantity = parseFloat(item.default_quantity) || 1.0;
    const calculatedMacros = calculateItemMacros(
      item.nutrients_per_100g,
      selectedUnit.gram_weight,
      selectedQuantity
    );

    return {
      ...item,
      food_name: item.display_name,
      predicted_dish_id: item.predicted_dish_id,
      final_dish_id: item.predicted_dish_id,
      label_modified: false,
      selectedUnitId,
      selectedUnit,
      selectedQuantity,
      calculatedMacros,
    };
  });
}

/**
 * Builds the canonical "Log Everything" telemetry payload conforming to backend contracts.
 */
export function buildTelemetryPayload(draft, mealType = 'lunch') {
  return {
    analysis_id: draft.analysis_id || `anlz_${Date.now().toString(16)}`,
    image_url: draft.image_url || 'https://storage.docta.ng/meals/captured_meal.jpg',
    meal_type: mealType,
    logged_at: new Date().toISOString(),
    items: (draft.items || []).map((item) => {
      const macros = item.calculatedMacros || calculateItemMacros(
        item.nutrients_per_100g,
        item.selectedUnit?.gram_weight || 100,
        item.selectedQuantity || 1
      );

      return {
        item_id: item.item_id,
        food_name: item.food_name || item.display_name,
        predicted_dish_id: item.predicted_dish_id,
        final_dish_id: item.final_dish_id || item.predicted_dish_id,
        label_modified: Boolean(item.label_modified),
        confidence: item.confidence || 0.9,
        bounding_box: item.bounding_box || [0, 0, 1, 1],
        selected_unit_id: item.selectedUnitId || item.selectedUnit?.unit_id,
        selected_quantity: parseFloat(item.selectedQuantity) || 1.0,
        gram_weight: macros.gramWeight,
        calories_kcal: macros.caloriesKcal,
        protein_g: macros.proteinG,
        fat_g: macros.fatG,
        carbs_g: macros.carbsG,
        fiber_g: macros.fiberG,
        sodium_mg: macros.sodiumMg,
        calcium_mg: macros.calciumMg,
        iron_mg: macros.ironMg,
      };
    }),
  };
}
