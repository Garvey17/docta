import test from 'node:test';
import assert from 'node:assert/strict';
import {
  calculateItemWeight,
  calculateItemNutrient,
  calculateItemMacros,
  calculateMealTotals,
  buildTelemetryPayload
} from '../src/utils/macroCalculator.js';

test('calculateItemWeight scales unit grams by quantity correctly', () => {
  // 120g serving spoon x 2.0 = 240g
  assert.equal(calculateItemWeight(120, 2), 240);
  // 25g slice x 6.0 = 150g
  assert.equal(calculateItemWeight(25, 6), 150);
  // 150g wrap x 1.5 = 225g
  assert.equal(calculateItemWeight(150, 1.5), 225);
});

test('calculateItemNutrient calculates (nutrient_per_100g / 100.0) * weight', () => {
  // 140 kcal per 100g on 240g weight = 336 kcal
  assert.equal(calculateItemNutrient(140.0, 240.0), 336.0);
  // 2.7g protein per 100g on 240g weight = 6.48g
  assert.equal(calculateItemNutrient(2.7, 240.0), 6.48);
  // 4.0g fat per 100g on 240g weight = 9.6g
  assert.equal(calculateItemNutrient(4.0, 240.0), 9.6);
  // 23.0g carbs per 100g on 240g weight = 55.2g
  assert.equal(calculateItemNutrient(23.0, 240.0), 55.2);
});

test('calculateItemMacros computes full macronutrient profile correctly', () => {
  const nutrients100g = {
    calories_kcal: 140.0,
    protein_g: 2.7,
    fat_g: 4.0,
    carbs_g: 23.0,
    fiber_g: 1.0,
    sodium_mg: 180.0,
    calcium_mg: 8.0,
    iron_mg: 0.7,
  };
  const result = calculateItemMacros(nutrients100g, 120.0, 2.0);
  assert.equal(result.gramWeight, 240.0);
  assert.equal(result.caloriesKcal, 336);
  assert.equal(result.proteinG, 6.48);
  assert.equal(result.fatG, 9.6);
  assert.equal(result.carbsG, 55.2);
  assert.equal(result.fiberG, 2.4);
  assert.equal(result.sodiumMg, 432);
});

test('calculateMealTotals sums up multi-food dishes accurately', () => {
  const items = [
    {
      calculatedMacros: {
        gramWeight: 240,
        caloriesKcal: 336,
        proteinG: 6.48,
        fatG: 9.6,
        carbsG: 55.2,
        fiberG: 2.4,
        sodiumMg: 432,
        calciumMg: 19.2,
        ironMg: 1.68,
      }
    },
    {
      calculatedMacros: {
        gramWeight: 150,
        caloriesKcal: 312,
        proteinG: 1.8,
        fatG: 14.1,
        carbsG: 48.0,
        fiberG: 3.6,
        sodiumMg: 6.0,
        calciumMg: 15.0,
        ironMg: 0.9,
      }
    }
  ];

  const totals = calculateMealTotals(items);
  assert.equal(totals.totalWeightG, 390);
  assert.equal(totals.totalCaloriesKcal, 648);
  assert.equal(Math.round(totals.totalProteinG * 100) / 100, 8.28);
  assert.equal(Math.round(totals.totalFatG * 100) / 100, 23.7);
  assert.equal(Math.round(totals.totalCarbsG * 100) / 100, 103.2);
});

test('buildTelemetryPayload conforms strictly to POST /api/v1/meals/log contract', () => {
  const mockDraft = {
    analysis_id: "anlz_8f92c10b",
    image_url: "https://storage.docta.ng/meals/temp_8f92c10b.jpg",
    items: [
      {
        item_id: "item_1",
        food_name: "Nigerian Jollof Rice",
        predicted_dish_id: "jollof_rice",
        final_dish_id: "jollof_rice",
        label_modified: false,
        confidence: 0.94,
        bounding_box: [0.125, 0.24, 0.55, 0.78],
        selectedUnitId: "serving_spoon",
        selectedQuantity: 2.0,
        calculatedMacros: {
          gramWeight: 240.0,
          caloriesKcal: 336.0,
          proteinG: 6.48,
          fatG: 9.6,
          carbsG: 55.2,
          fiberG: 2.4,
          sodiumMg: 432.0,
          calciumMg: 19.2,
          ironMg: 1.68
        }
      }
    ]
  };

  const payload = buildTelemetryPayload(mockDraft, 'lunch');
  assert.equal(payload.analysis_id, "anlz_8f92c10b");
  assert.equal(payload.meal_type, "lunch");
  assert.equal(payload.items.length, 1);
  assert.equal(payload.items[0].predicted_dish_id, "jollof_rice");
  assert.equal(payload.items[0].selected_unit_id, "serving_spoon");
  assert.equal(payload.items[0].selected_quantity, 2.0);
  assert.equal(payload.items[0].gram_weight, 240.0);
  assert.equal(payload.items[0].calories_kcal, 336.0);
});
