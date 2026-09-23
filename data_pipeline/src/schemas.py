"""Pydantic v2 schemas for the data_pipeline sub-team."""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class NutrientProfile(BaseModel):
    """Standardized nutritional metrics for 100g or scaled portions."""
    model_config = ConfigDict(extra="ignore")

    calories_kcal: float = Field(..., description="Energy in kilocalories (kcal)")
    protein_g: float = Field(..., description="Protein in grams (g)")
    fat_g: float = Field(..., description="Total lipids / fat in grams (g)")
    carbs_g: float = Field(..., description="Available carbohydrates in grams (g)")
    fiber_g: float = Field(0.0, description="Dietary fiber in grams (g)")
    sodium_mg: float = Field(0.0, description="Sodium in milligrams (mg)")
    calcium_mg: float = Field(0.0, description="Calcium in milligrams (mg)")
    iron_mg: float = Field(0.0, description="Iron in milligrams (mg)")

    def round_values(self, decimals: int = 1) -> "NutrientProfile":
        """Return a new NutrientProfile with all numeric fields rounded."""
        return NutrientProfile(
            calories_kcal=round(self.calories_kcal, decimals),
            protein_g=round(self.protein_g, decimals),
            fat_g=round(self.fat_g, decimals),
            carbs_g=round(self.carbs_g, decimals),
            fiber_g=round(self.fiber_g, decimals),
            sodium_mg=round(self.sodium_mg, decimals),
            calcium_mg=round(self.calcium_mg, decimals),
            iron_mg=round(self.iron_mg, decimals),
        )


class Ingredient(BaseModel):
    """Constituent raw ingredient with code and mass in grams."""
    model_config = ConfigDict(extra="ignore")

    ingredient_code: str
    name: str
    quantity_g: float = Field(..., ge=0.0)


class Recipe(BaseModel):
    """Recipe-Ingredient-Quantity (RIQ) definition for a dish."""
    model_config = ConfigDict(extra="ignore")

    dish_id: str
    dish_name: str
    standard_serving_g: float = Field(..., gt=0.0)
    cooking_yield_factor: float = Field(..., gt=0.0)
    ingredients: List[Ingredient]


class RecipeIngredientLookup(BaseModel):
    """Collection of standardized recipes."""
    model_config = ConfigDict(extra="ignore")

    recipes: List[Recipe]


class FoodItemFCT(BaseModel):
    """Individual food item record from Food Composition Table (per 100g raw)."""
    model_config = ConfigDict(extra="ignore")

    code: str
    food_name: str
    nutrients: NutrientProfile


class CompositeDish(BaseModel):
    """Compiled composite dish record with raw & cooked per-100g nutrient profiles."""
    model_config = ConfigDict(extra="ignore")

    dish_id: str
    dish_name: str
    standard_serving_g: float
    cooking_yield_factor: float
    raw_batch_mass_g: float
    raw_ingredients: List[Ingredient]
    nutrients_raw_100g: NutrientProfile
    nutrients_cooked_100g: NutrientProfile
    wafct_code: str = "WAFCT_COMPOSITE"
    description: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)


class ScaledItemNutrition(BaseModel):
    """Itemized scaled nutrition output aligned with PROJECT_ORCHESTRATION.md."""
    model_config = ConfigDict(extra="ignore")

    item_id: Optional[str] = None
    dish_id: str
    display_name: str
    confidence: float = 1.0
    bounding_box: Optional[List[float]] = None
    weight_g: float
    wafct_code: str
    similarity_score: float
    is_fallback: bool = False
    nutrients: NutrientProfile


class TotalNutrition(BaseModel):
    """Aggregated nutritional summary for a full meal."""
    model_config = ConfigDict(extra="ignore")

    total_calories_kcal: float
    total_protein_g: float
    total_fat_g: float
    total_carbs_g: float
    total_fiber_g: float
    total_sodium_mg: float
    total_calcium_mg: float
    total_iron_mg: float

    def round_values(self, decimals: int = 1) -> "TotalNutrition":
        """Return a new TotalNutrition with all values rounded."""
        return TotalNutrition(
            total_calories_kcal=round(self.total_calories_kcal, decimals),
            total_protein_g=round(self.total_protein_g, decimals),
            total_fat_g=round(self.total_fat_g, decimals),
            total_carbs_g=round(self.total_carbs_g, decimals),
            total_fiber_g=round(self.total_fiber_g, decimals),
            total_sodium_mg=round(self.total_sodium_mg, decimals),
            total_calcium_mg=round(self.total_calcium_mg, decimals),
            total_iron_mg=round(self.total_iron_mg, decimals),
        )


class MealAnalysisResponse(BaseModel):
    """Full meal response contract matching PROJECT_ORCHESTRATION.md Section 6.2 B."""
    model_config = ConfigDict(extra="ignore")

    analysis_id: str
    status: str = "success"
    processing_duration_ms: float
    image_url: Optional[str] = None
    detected_items: List[ScaledItemNutrition]
    total_nutrition: TotalNutrition


class MealItemInput(BaseModel):
    """Input payload for a detected meal item to be enriched by RAG service."""
    model_config = ConfigDict(extra="ignore")

    dish_id: Optional[str] = None
    dish_name: Optional[str] = None
    query: Optional[str] = None
    weight_g: float
    item_id: Optional[str] = None
    confidence: float = 1.0
    bounding_box: Optional[List[float]] = None
