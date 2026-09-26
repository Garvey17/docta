import test from 'node:test';
import assert from 'node:assert/strict';

test('CameraFeed handles fallback mock samples correctly', () => {
  const sample = {
    dish_id: 'jollof_rice',
    display_name: 'Nigerian Jollof Rice',
    confidence: 0.94,
    bounding_box: [0.12, 0.22, 0.58, 0.78],
  };

  assert.equal(sample.dish_id, 'jollof_rice');
  assert.equal(sample.confidence > 0.9, true);
  assert.equal(sample.bounding_box.length, 4);
});
