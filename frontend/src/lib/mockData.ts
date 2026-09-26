import { AnalyzeMealResponse, UserProfile, MealHistoryRecord } from '../types/api';

export const MOCK_USER: UserProfile = {
  id: "usr_4a89fb21",
  name: "Balkisu Habib",
  email: "balkisu@docta.ng",
  dailyCalorieTarget: 2200,
  dailyProteinTargetG: 110,
  dailyCarbsTargetG: 250,
  dailyFatTargetG: 65,
  dailyFiberTargetG: 30,
  dailySodiumTargetMg: 2300,
};

export const MOCK_ANALYZE_RESPONSE: AnalyzeMealResponse = {
  analysis_id: "anlz_8f92c10b",
  status: "success",
  processing_duration_ms: 780.2,
  image_url: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80",
  detected_items: [
    {
      item_id: "item_1",
      predicted_dish_id: "jollof_rice",
      display_name: "Nigerian Jollof Rice",
      confidence: 0.94,
      bounding_box: [0.12, 0.22, 0.58, 0.78],
      default_unit_id: "serving_spoon",
      default_quantity: 2.0,
      default_weight_g: 240.0,
      available_portion_units: [
        {
          unit_id: "serving_spoon",
          unit_name: "Serving Spoon",
          gram_weight: 120.0,
          description: "Standard catering/cooking spoon (~120g)"
        },
        {
          unit_id: "mound_cup",
          unit_name: "Mound / Cup",
          gram_weight: 250.0,
          description: "Standard dining plate mound (~250g)"
        },
        {
          unit_id: "takeaway_pack",
          unit_name: "Takeaway Pack",
          gram_weight: 500.0,
          description: "Full standard plastic takeaway pack (~500g)"
        }
      ],
      nutrients_per_100g: {
        calories_kcal: 140.0,
        protein_g: 2.7,
        fat_g: 4.0,
        carbs_g: 23.0,
        fiber_g: 1.0,
        sodium_mg: 180.0,
        calcium_mg: 8.0,
        iron_mg: 0.7
      }
    },
    {
      item_id: "item_2",
      predicted_dish_id: "fried_plantain",
      display_name: "Fried Ripe Plantain (Dodo)",
      confidence: 0.89,
      bounding_box: [0.55, 0.28, 0.90, 0.68],
      default_unit_id: "portion_6_slices",
      default_quantity: 1.0,
      default_weight_g: 150.0,
      available_portion_units: [
        {
          unit_id: "single_slice",
          unit_name: "Single Slice / Piece",
          gram_weight: 25.0,
          description: "One slice (~25g)"
        },
        {
          unit_id: "portion_6_slices",
          unit_name: "Small Portion (6 slices)",
          gram_weight: 150.0,
          description: "Standard side portion (~150g)"
        },
        {
          unit_id: "large_portion",
          unit_name: "Large Portion (12 slices)",
          gram_weight: 300.0,
          description: "Double side portion (~300g)"
        }
      ],
      nutrients_per_100g: {
        calories_kcal: 208.0,
        protein_g: 1.2,
        fat_g: 9.4,
        carbs_g: 32.0,
        fiber_g: 2.4,
        sodium_mg: 4.0,
        calcium_mg: 10.0,
        iron_mg: 0.6
      }
    }
  ]
};

export const MOCK_ALTERNATIVE_ANALYSIS: AnalyzeMealResponse = {
  analysis_id: "anlz_73bc92e1",
  status: "success",
  processing_duration_ms: 640.5,
  image_url: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80",
  detected_items: [
    {
      item_id: "item_alt_1",
      predicted_dish_id: "amala",
      display_name: "Amala (Yam Flour Swallow)",
      confidence: 0.92,
      bounding_box: [0.15, 0.20, 0.52, 0.75],
      default_unit_id: "medium_wrap",
      default_quantity: 1.0,
      default_weight_g: 250.0,
      available_portion_units: [
        { unit_id: "small_wrap", unit_name: "Small Wrap", gram_weight: 150.0, description: "Light portion (~150g)" },
        { unit_id: "medium_wrap", unit_name: "Medium Wrap", gram_weight: 250.0, description: "Standard restaurant wrap (~250g)" },
        { unit_id: "large_wrap", unit_name: "Large Wrap", gram_weight: 400.0, description: "Heavy portion (~400g)" }
      ],
      nutrients_per_100g: {
        calories_kcal: 110.0,
        protein_g: 1.5,
        fat_g: 0.3,
        carbs_g: 25.4,
        fiber_g: 3.2,
        sodium_mg: 12.0,
        calcium_mg: 14.0,
        iron_mg: 1.1
      }
    },
    {
      item_id: "item_alt_2",
      predicted_dish_id: "egusi_soup",
      display_name: "Egusi Melon Seed Soup",
      confidence: 0.96,
      bounding_box: [0.52, 0.25, 0.92, 0.82],
      default_unit_id: "serving_spoon",
      default_quantity: 2.0,
      default_weight_g: 200.0,
      available_portion_units: [
        { unit_id: "serving_spoon", unit_name: "Serving Spoon", gram_weight: 100.0, description: "Standard soup spoon (~100g)" },
        { unit_id: "small_bowl", unit_name: "Small Soup Bowl", gram_weight: 200.0, description: "Side soup bowl (~200g)" },
        { unit_id: "large_bowl", unit_name: "Large Soup Bowl", gram_weight: 350.0, description: "Main soup bowl (~350g)" }
      ],
      nutrients_per_100g: {
        calories_kcal: 220.0,
        protein_g: 8.5,
        fat_g: 17.0,
        carbs_g: 8.2,
        fiber_g: 3.8,
        sodium_mg: 340.0,
        calcium_mg: 45.0,
        iron_mg: 2.8
      }
    }
  ]
};

export const MOCK_MEAL_HISTORY: MealHistoryRecord[] = [
  {
    meal_id: "meal_01",
    meal_type: "breakfast",
    logged_at: new Date(Date.now() - 4 * 3600 * 1000).toISOString(),
    total_calories_kcal: 312,
    total_protein_g: 18.2,
    total_carbs_g: 34.0,
    total_fat_g: 11.5,
    items: [
      {
        food_name: "Steamed Bean Cake (Moi Moi)",
        unit_name: "Single Leaf Wrap",
        quantity: 1.0,
        gram_weight: 150.0,
        calories_kcal: 215
      },
      {
        food_name: "Cornmeal Pap (Ogi)",
        unit_name: "Small Bowl",
        quantity: 1.0,
        gram_weight: 200.0,
        calories_kcal: 97
      }
    ]
  },
  {
    meal_id: "meal_02",
    meal_type: "lunch",
    logged_at: new Date(Date.now() - 1 * 3600 * 1000).toISOString(),
    total_calories_kcal: 648,
    total_protein_g: 8.28,
    total_carbs_g: 103.2,
    total_fat_g: 23.7,
    items: [
      {
        food_name: "Nigerian Jollof Rice",
        unit_name: "Serving Spoon",
        quantity: 2.0,
        gram_weight: 240.0,
        calories_kcal: 336
      },
      {
        food_name: "Fried Ripe Plantain (Dodo)",
        unit_name: "Small Portion (6 slices)",
        quantity: 1.0,
        gram_weight: 150.0,
        calories_kcal: 312
      }
    ]
  }
];
