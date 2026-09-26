/**
 * Macro & Nutrition Calculator
 * Linear scaling based on WAFCT nutrient composition per 100g.
 * Formula:
 *   Item Weight (g) = unit_gram_weight * quantity
 *   Item Nutrient = (nutrient_per_100g / 100.0) * item_weight_g
 */

export function calculateItemWeight(unitGramWeight, quantity) {
  const g = (parseFloat(unitGramWeight) || 0) * (parseFloat(quantity) || 0);
  return Math.round(g * 10) / 10;
}

export function calculateItemNutrient(per100g, weightGrams) {
  const p100 = parseFloat(per100g) || 0;
  const weight = parseFloat(weightGrams) || 0;
  const val = (p100 / 100.0) * weight;
  return Math.round(val * 100) / 100;
}

export function calculateItemMacros(nutrientsPer100g = {}, unitGramWeight = 0, quantity = 1.0) {
  const gramWeight = calculateItemWeight(unitGramWeight, quantity);
  return {
    gramWeight,
    caloriesKcal: Math.round(calculateItemNutrient(nutrientsPer100g.calories_kcal, gramWeight)),
    proteinG: calculateItemNutrient(nutrientsPer100g.protein_g, gramWeight),
    fatG: calculateItemNutrient(nutrientsPer100g.fat_g, gramWeight),
    carbsG: calculateItemNutrient(nutrientsPer100g.carbs_g, gramWeight),
    fiberG: calculateItemNutrient(nutrientsPer100g.fiber_g, gramWeight),
    sodiumMg: Math.round(calculateItemNutrient(nutrientsPer100g.sodium_mg, gramWeight)),
    calciumMg: calculateItemNutrient(nutrientsPer100g.calcium_mg, gramWeight),
    ironMg: calculateItemNutrient(nutrientsPer100g.iron_mg, gramWeight),
  };
}

export function calculateMealTotals(items = []) {
  return items.reduce(
    (acc, item) => {
      const macros = item.calculatedMacros || calculateItemMacros(
        item.nutrients_per_100g,
        item.selectedUnit?.gram_weight || item.default_weight_g || 100,
        item.selectedQuantity || item.default_quantity || 1.0
      );

      acc.totalWeightG += macros.gramWeight || 0;
      acc.totalCaloriesKcal += macros.caloriesKcal || 0;
      acc.totalProteinG += macros.proteinG || 0;
      acc.totalFatG += macros.fatG || 0;
      acc.totalCarbsG += macros.carbsG || 0;
      acc.totalFiberG += macros.fiberG || 0;
      acc.totalSodiumMg += macros.sodiumMg || 0;
      acc.totalCalciumMg += macros.calciumMg || 0;
      acc.totalIronMg += macros.ironMg || 0;
      return acc;
    },
    {
      totalWeightG: 0,
      totalCaloriesKcal: 0,
      totalProteinG: 0,
      totalFatG: 0,
      totalCarbsG: 0,
      totalFiberG: 0,
      totalSodiumMg: 0,
      totalCalciumMg: 0,
      totalIronMg: 0,
    }
  );
}

export function buildTelemetryPayload(draft, mealType = 'lunch') {
  const items = (draft.items || []).map((item) => {
    const macros = item.calculatedMacros || calculateItemMacros(
      item.nutrients_per_100g,
      item.selectedUnit?.gram_weight || item.gram_weight || 100,
      item.selectedQuantity || 1.0
    );

    const selectedUnitId = item.selectedUnitId || item.selected_unit_id || item.selectedUnit?.unit_id || item.default_unit_id || 'serving_spoon';
    const selectedQuantity = Number(item.selectedQuantity ?? item.selected_quantity ?? item.default_quantity ?? 1.0);
    const gramWeight = macros.gramWeight ?? (item.gram_weight || 100);
    const caloriesKcal = macros.caloriesKcal ?? (item.calories_kcal || 0);
    const proteinG = macros.proteinG ?? (item.protein_g || 0);
    const fatG = macros.fatG ?? (item.fat_g || 0);
    const carbsG = macros.carbsG ?? (item.carbs_g || 0);
    const fiberG = macros.fiberG ?? (item.fiber_g || 0);
    const sodiumMg = macros.sodiumMg ?? (item.sodium_mg || 0);
    const calciumMg = macros.calciumMg ?? (item.calcium_mg || 0);
    const ironMg = macros.ironMg ?? (item.iron_mg || 0);

    return {
      item_id: item.item_id || item.itemId,
      food_name: item.food_name || item.foodName || item.display_name,
      predicted_dish_id: item.predicted_dish_id || item.predictedDishId,
      final_dish_id: item.final_dish_id || item.finalDishId || item.predicted_dish_id,
      label_modified: Boolean(item.label_modified ?? item.labelModified),
      confidence: item.confidence ?? 0.9,
      bounding_box: item.bounding_box || item.boundingBox || [0, 0, 1, 1],
      selected_unit_id: selectedUnitId,
      selected_quantity: selectedQuantity,
      gram_weight: gramWeight,
      calories_kcal: caloriesKcal,
      protein_g: proteinG,
      fat_g: fatG,
      carbs_g: carbsG,
      fiber_g: fiberG,
      sodium_mg: sodiumMg,
      calcium_mg: calciumMg,
      iron_mg: ironMg,

      itemId: item.item_id || item.itemId,
      foodName: item.food_name || item.foodName || item.display_name,
      predictedDishId: item.predicted_dish_id || item.predictedDishId,
      finalDishId: item.final_dish_id || item.finalDishId || item.predicted_dish_id,
      labelModified: Boolean(item.label_modified ?? item.labelModified),
      boundingBox: item.bounding_box || item.boundingBox || [0, 0, 1, 1],
      selectedUnitId: selectedUnitId,
      selectedQuantity: selectedQuantity,
      gramWeight: gramWeight,
      caloriesKcal: caloriesKcal,
      proteinG: proteinG,
      fatG: fatG,
      carbsG: carbsG,
      fiberG: fiberG,
      sodiumMg: sodiumMg,
      calciumMg: calciumMg,
      ironMg: ironMg,
    };
  });

  return {
    analysis_id: draft.analysis_id || draft.analysisId || `anlz_${Date.now().toString(16)}`,
    image_url: draft.image_url || draft.imageUrl || 'https://storage.docta.ng/meals/captured.jpg',
    meal_type: mealType || draft.meal_type || draft.mealType || 'lunch',
    logged_at: draft.logged_at || new Date().toISOString(),
    items,
  };
}

