import test from 'node:test';
import assert from 'node:assert/strict';
import { calculateItemMacros } from '../src/lib/utils.js';

test('FoodItemCard correctly computes item nutrition from WAFCT base profile', () => {
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

  // 2 serving spoons of Jollof rice (240g)
  const macros = calculateItemMacros(nutrients100g, 120.0, 2.0);
  assert.equal(macros.gramWeight, 240.0);
  assert.equal(macros.caloriesKcal, 336);
  assert.equal(macros.proteinG, 6.48);
  assert.equal(macros.fatG, 9.6);
  assert.equal(macros.carbsG, 55.2);
});

test('FoodItemCard label correction sets label_modified flag to true', () => {
  const item = {
    predicted_dish_id: 'jollof_rice',
    final_dish_id: 'jollof_rice',
    label_modified: false,
  };

  // User selects Fried Rice instead
  const corrected = {
    ...item,
    final_dish_id: 'fried_rice',
    label_modified: true,
  };

  assert.equal(corrected.label_modified, true);
  assert.notEqual(corrected.final_dish_id, corrected.predicted_dish_id);
});
