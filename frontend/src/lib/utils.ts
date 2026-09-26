import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { NutrientProfile } from '../types/api';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function calculateItemWeight(unitGramWeight: number, quantity: number): number {
  const g = (Number(unitGramWeight) || 0) * (Number(quantity) || 0);
  return Math.round(g * 10) / 10;
}

export function calculateItemNutrient(per100g: number, weightGrams: number): number {
  const p100 = Number(per100g) || 0;
  const weight = Number(weightGrams) || 0;
  const val = (p100 / 100.0) * weight;
  return Math.round(val * 100) / 100;
}

export function calculateItemMacros(
  nutrientsPer100g: NutrientProfile,
  unitGramWeight: number = 0,
  quantity: number = 1.0
) {
  const gramWeight = calculateItemWeight(unitGramWeight, quantity);
  return {
    gramWeight,
    caloriesKcal: Math.round(calculateItemNutrient(nutrientsPer100g?.calories_kcal || 0, gramWeight)),
    proteinG: calculateItemNutrient(nutrientsPer100g?.protein_g || 0, gramWeight),
    fatG: calculateItemNutrient(nutrientsPer100g?.fat_g || 0, gramWeight),
    carbsG: calculateItemNutrient(nutrientsPer100g?.carbs_g || 0, gramWeight),
    fiberG: calculateItemNutrient(nutrientsPer100g?.fiber_g || 0, gramWeight),
    sodiumMg: Math.round(calculateItemNutrient(nutrientsPer100g?.sodium_mg || 0, gramWeight)),
    calciumMg: calculateItemNutrient(nutrientsPer100g?.calcium_mg || 0, gramWeight),
    ironMg: calculateItemNutrient(nutrientsPer100g?.iron_mg || 0, gramWeight),
  };
}

export function formatGrams(val: number): string {
  return `${Math.round((Number(val) || 0) * 10) / 10}g`;
}

export function formatCalories(val: number): string {
  return `${Math.round(Number(val) || 0)} kcal`;
}

export function formatMg(val: number): string {
  return `${Math.round(Number(val) || 0)} mg`;
}

export function formatConfidence(confidence: number): string {
  const pct = Math.round((Number(confidence) || 0) * 100);
  return `${pct}% match`;
}

export function formatTimeAgo(isoString: string): string {
  if (!isoString) return '';
  const date = new Date(isoString);
  const now = new Date();
  const diffMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
  if (diffMinutes < 1) return 'Just now';
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
}
