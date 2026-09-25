export function formatGrams(val) {
  const n = parseFloat(val) || 0;
  return `${Math.round(n * 10) / 10}g`;
}

export function formatCalories(val) {
  const n = Math.round(parseFloat(val) || 0);
  return `${n} kcal`;
}

export function formatMg(val) {
  const n = Math.round(parseFloat(val) || 0);
  return `${n} mg`;
}

export function formatConfidence(confidence) {
  const pct = Math.round((parseFloat(confidence) || 0) * 100);
  return `${pct}% match`;
}

export function formatTimeAgo(isoString) {
  if (!isoString) return '';
  const date = new Date(isoString);
  const now = new Date();
  const diffMinutes = Math.floor((now - date) / (1000 * 60));
  if (diffMinutes < 1) return 'Just now';
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
}
