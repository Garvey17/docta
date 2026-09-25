/**
 * UI Color Tokens & Formatting
 * Aligned with the design system from Abdulrazak-Abdulsamad/Funding-Ai-App frontend.
 */

export const SUMMARY_CARD_COLOR_CLASSES = {
  indigo: 'border-indigo-200 bg-indigo-50/50 text-indigo-900 hover:border-indigo-300',
  green: 'border-emerald-200 bg-emerald-50/50 text-emerald-900 hover:border-emerald-300',
  amber: 'border-amber-200 bg-amber-50/50 text-amber-900 hover:border-amber-300',
  red: 'border-rose-200 bg-rose-50/50 text-rose-900 hover:border-rose-300',
  purple: 'border-purple-200 bg-purple-50/50 text-purple-900 hover:border-purple-300',
};

export const MACRO_COLORS = {
  calories: {
    stroke: '#5B50E5',
    bg: 'bg-indigo-600',
    text: 'text-indigo-600',
    light: 'bg-indigo-50',
    border: 'border-indigo-200',
    label: 'Calories',
  },
  protein: {
    stroke: '#3B82F6',
    bg: 'bg-blue-600',
    text: 'text-blue-600',
    light: 'bg-blue-50',
    border: 'border-blue-200',
    label: 'Protein',
  },
  carbs: {
    stroke: '#F59E0B',
    bg: 'bg-amber-500',
    text: 'text-amber-600',
    light: 'bg-amber-50',
    border: 'border-amber-200',
    label: 'Carbs',
  },
  fat: {
    stroke: '#F43F5E',
    bg: 'bg-rose-500',
    text: 'text-rose-600',
    light: 'bg-rose-50',
    border: 'border-rose-200',
    label: 'Fat',
  },
  fiber: {
    stroke: '#10B981',
    bg: 'bg-emerald-500',
    text: 'text-emerald-600',
    light: 'bg-emerald-50',
    border: 'border-emerald-200',
    label: 'Fiber',
  },
};

export function getCalorieStatusColor(current, target) {
  const ratio = (current / target) * 100;
  if (ratio <= 90) return 'text-emerald-600';
  if (ratio <= 105) return 'text-indigo-600';
  if (ratio <= 120) return 'text-amber-500';
  return 'text-rose-500';
}
