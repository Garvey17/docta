/**
 * Shared API Contracts & Data Types
 * Sourced directly from /frontend/INSTRUCTION.md & /PROJECT_ORCHESTRATION.md
 */

export interface PortionUnit {
  unit_id: string;
  unit_name: string;
  gram_weight: number;
  description: string;
}

export interface NutrientProfile {
  calories_kcal: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
  fiber_g: number;
  sodium_mg: number;
  calcium_mg: number;
  iron_mg: number;
}

export interface DetectedFoodItem {
  item_id: string;
  predicted_dish_id: string;
  display_name: string;
  confidence: number;
  bounding_box: [number, number, number, number];
  default_unit_id: string;
  default_quantity: number;
  default_weight_g: number;
  available_portion_units: PortionUnit[];
  nutrients_per_100g: NutrientProfile;
}

export interface AnalyzeMealResponse {
  analysis_id: string;
  status: string;
  processing_duration_ms: number;
  image_url: string;
  detected_items: DetectedFoodItem[];
}

/**
 * Section 4: "Log Everything" Telemetry Payload Interface
 */
export interface LogMealItemPayload {
  itemId: string;
  foodName: string;
  predictedDishId: string;
  finalDishId: string;
  labelModified: boolean;
  confidence: number;
  boundingBox: [number, number, number, number];
  selectedUnitId: string;
  selectedQuantity: number;
  gramWeight: number;
  caloriesKcal: number;
  proteinG: number;
  fatG: number;
  carbsG: number;
  fiberG: number;
  sodiumMg: number;
  calciumMg: number;
  ironMg: number;
}

export interface LogMealPayload {
  analysis_id: string;
  image_url: string;
  meal_type: string;
  logged_at: string;
  items: LogMealItemPayload[];
}

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  dailyCalorieTarget: number;
  dailyProteinTargetG: number;
  dailyCarbsTargetG: number;
  dailyFatTargetG: number;
  dailyFiberTargetG: number;
  dailySodiumTargetMg: number;
}

export interface MealHistoryRecord {
  meal_id: string;
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  logged_at: string;
  total_calories_kcal: number;
  total_protein_g: number;
  total_carbs_g: number;
  total_fat_g: number;
  items: Array<{
    food_name: string;
    unit_name: string;
    quantity: number;
    gram_weight: number;
    calories_kcal: number;
  }>;
}
