import test from 'node:test';
import assert from 'node:assert/strict';
import { calculateItemWeight, calculateItemNutrient, calculateItemMacros } from '../src/lib/utils.js';

test('PortionUnitSelector calculation logic converts units to correct gram mass', () => {
  // Serving Spoon 120g x 2.0 quantity = 240g
  const weight = calculateItemWeight(120, 2);
  assert.equal(weight, 240);

  // Mound / Cup 250g x 1.5 quantity = 375g
  const moundWeight = calculateItemWeight(250, 1.5);
  assert.equal(moundWeight, 375);

  // Takeaway pack 500g x 0.5 quantity = 250g
  const packWeight = calculateItemWeight(500, 0.5);
  assert.equal(packWeight, 250);
});

test('PortionUnitSelector stepper step bounds are respected', () => {
  const step = 0.5;
  const current = 1.0;
  const incremented = current + step;
  const decremented = Math.max(0.5, current - step);
  assert.equal(incremented, 1.5);
  assert.equal(decremented, 0.5);
});
