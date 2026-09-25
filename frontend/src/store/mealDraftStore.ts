import { create } from 'zustand';
import {
  AnalyzeMealResponse,
  DetectedFoodItem,
  LogMealItemPayload,
  LogMealPayload,
  PortionUnit,
} from '../types/api';
import { calculateItemMacros } from '../lib/utils';

export interface DraftItem extends DetectedFoodItem {
  food_name: string;
  final_dish_id: string;
  label_modified: boolean;
  selectedUnitId: string;
  selectedUnit: PortionUnit;
  selectedQuantity: number;
  calculatedMacros: ReturnType<typeof calculateItemMacros>;
}

interface MealDraftState {
  analysisId: string | null;
  imageUrl: string | null;
  mealType: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  items: DraftItem[];
  activeItemId: string | null;

  setMealType: (type: 'breakfast' | 'lunch' | 'dinner' | 'snack') => void;
  setActiveItemId: (id: string | null) => void;
  setDraft: (analysis: AnalyzeMealResponse, customImageUrl?: string) => void;
  updatePortion: (itemId: string, unitId: string, quantity: number) => void;
  updateLabel: (itemId: string, newFoodName: string, newDishId: string, newUnits?: PortionUnit[]) => void;
  removeItem: (itemId: string) => void;
  addItem: (item: DraftItem) => void;
  clearDraft: () => void;
  getTelemetryPayload: () => LogMealPayload;
}

export const useMealDraftStore = create<MealDraftState>((set, get) => ({
  analysisId: null,
  imageUrl: null,
  mealType: 'lunch',
  items: [],
  activeItemId: null,

  setMealType: (mealType) => set({ mealType }),

  setActiveItemId: (activeItemId) => set({ activeItemId }),

  setDraft: (analysis, customImageUrl) => {
    const items: DraftItem[] = (analysis.detected_items || []).map((item) => {
      const selectedUnitId = item.default_unit_id || item.available_portion_units?.[0]?.unit_id || 'serving_spoon';
      const selectedUnit = item.available_portion_units?.find((u) => u.unit_id === selectedUnitId) ||
        item.available_portion_units?.[0] || {
          unit_id: selectedUnitId,
          unit_name: 'Standard Portion',
          gram_weight: item.default_weight_g || 150.0,
          description: 'Standard portion'
        };

      const selectedQuantity = Number(item.default_quantity) || 1.0;
      const calculatedMacros = calculateItemMacros(
        item.nutrients_per_100g,
        selectedUnit.gram_weight,
        selectedQuantity
      );

      return {
        ...item,
        food_name: item.display_name,
        final_dish_id: item.predicted_dish_id,
        label_modified: false,
        selectedUnitId,
        selectedUnit,
        selectedQuantity,
        calculatedMacros,
      };
    });

    set({
      analysisId: analysis.analysis_id,
      imageUrl: customImageUrl || analysis.image_url,
      items,
      activeItemId: items[0]?.item_id || null,
    });
  },

  updatePortion: (itemId, unitId, quantity) => {
    set((state) => ({
      items: state.items.map((item) => {
        if (item.item_id !== itemId) return item;
        const unit = item.available_portion_units?.find((u) => u.unit_id === unitId) || item.selectedUnit;
        const macros = calculateItemMacros(item.nutrients_per_100g, unit?.gram_weight || 100, quantity);
        return {
          ...item,
          selectedUnitId: unitId,
          selectedUnit: unit,
          selectedQuantity: quantity,
          calculatedMacros: macros,
        };
      }),
    }));
  },

  updateLabel: (itemId, newFoodName, newDishId, newUnits) => {
    set((state) => ({
      items: state.items.map((item) => {
        if (item.item_id !== itemId) return item;
        const availableUnits = newUnits || item.available_portion_units;
        const selectedUnit = availableUnits?.[0] || item.selectedUnit;
        const macros = calculateItemMacros(
          item.nutrients_per_100g,
          selectedUnit.gram_weight,
          item.selectedQuantity
        );

        return {
          ...item,
          food_name: newFoodName,
          final_dish_id: newDishId,
          label_modified: true,
          available_portion_units: availableUnits,
          selectedUnitId: selectedUnit.unit_id,
          selectedUnit,
          calculatedMacros: macros,
        };
      }),
    }));
  },

  removeItem: (itemId) => {
    set((state) => ({
      items: state.items.filter((item) => item.item_id !== itemId),
    }));
  },

  addItem: (item) => {
    set((state) => ({
      items: [...state.items, item],
    }));
  },

  clearDraft: () => {
    set({
      analysisId: null,
      imageUrl: null,
      items: [],
      activeItemId: null,
    });
  },

  getTelemetryPayload: () => {
    const state = get();
    return buildTelemetryPayload(
      {
        analysisId: state.analysisId,
        imageUrl: state.imageUrl,
        items: state.items,
      },
      state.mealType
    );
  },
}));

export function buildTelemetryPayload(
  draft: {
    analysisId?: string | null;
    analysis_id?: string;
    imageUrl?: string | null;
    image_url?: string;
    items: any[];
  },
  mealType: string = 'lunch'
): LogMealPayload {
  const itemsPayload: LogMealItemPayload[] = (draft.items || []).map((item) => {
    const macros = item.calculatedMacros || calculateItemMacros(
      item.nutrients_per_100g,
      item.selectedUnit?.gram_weight || item.gram_weight || 100,
      item.selectedQuantity || 1.0
    );
    const selectedUnitId = item.selectedUnitId || item.selected_unit_id || item.selectedUnit?.unit_id || 'serving_spoon';
    const selectedQuantity = Number(item.selectedQuantity ?? item.selected_quantity ?? 1.0);
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
      itemId: item.item_id || item.itemId,
      foodName: item.food_name || item.foodName || item.display_name,
      predictedDishId: item.predicted_dish_id || item.predictedDishId,
      finalDishId: item.final_dish_id || item.finalDishId || item.predicted_dish_id,
      labelModified: Boolean(item.label_modified ?? item.labelModified),
      confidence: item.confidence ?? 0.9,
      boundingBox: item.bounding_box || item.boundingBox || [0, 0, 1, 1],
      selectedUnitId,
      selectedQuantity,
      gramWeight,
      caloriesKcal,
      proteinG,
      fatG,
      carbsG,
      fiberG,
      sodiumMg,
      calciumMg,
      ironMg,

      // snake_case aliases for backend ingestion compatibility
      item_id: item.item_id || item.itemId,
      food_name: item.food_name || item.foodName || item.display_name,
      predicted_dish_id: item.predicted_dish_id || item.predictedDishId,
      final_dish_id: item.final_dish_id || item.finalDishId || item.predicted_dish_id,
      label_modified: Boolean(item.label_modified ?? item.labelModified),
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
    } as LogMealItemPayload;
  });

  return {
    analysis_id: draft.analysis_id || draft.analysisId || `anlz_${Date.now().toString(16)}`,
    image_url: draft.image_url || draft.imageUrl || 'https://storage.docta.ng/meals/captured.jpg',
    meal_type: mealType,
    logged_at: new Date().toISOString(),
    items: itemsPayload,
  };
}
