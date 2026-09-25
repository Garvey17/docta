import test from 'node:test';
import assert from 'node:assert/strict';

test('BoundingOverlay normalizes coordinates properly', () => {
  const box = [0.12, 0.22, 0.58, 0.78];
  const leftPct = Math.round(Math.min(box[0], box[2]) * 100);
  const topPct = Math.round(Math.min(box[1], box[3]) * 100);
  const widthPct = Math.round(Math.abs(box[2] - box[0]) * 100);
  const heightPct = Math.round(Math.abs(box[3] - box[1]) * 100);

  assert.equal(leftPct, 12);
  assert.equal(topPct, 22);
  assert.equal(widthPct, 46);
  assert.equal(heightPct, 56);
});
