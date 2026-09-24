"""Simplified Pydantic v2 data models for docta Data & RAG pipeline."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class NutrientProfile(BaseModel):
    """Nutritional metrics for 100g or scaled meal portions."""
    model_config = ConfigDict(extra="ignore")

    calories_kcal: float = Field(0.0, description="Energy (kcal)")
    protein_g: float = Field(0.0, description="Protein (g)")
    fat_g: float = Field(0.0, description="Total Lipids/Fat (g)")
    carbs_g: float = Field(0.0, description="Carbohydrates (g)")
    fiber_g: float = Field(0.0, description="Dietary Fiber (g)")
    sodium_mg: float = Field(0.0, description="Sodium (mg)")
    calcium_mg: float = Field(0.0, description="Calcium (mg)")
    iron_mg: float = Field(0.0, description="Iron (mg)")

    def round_values(self, decimals: int = 1) -> "NutrientProfile":
        """Return rounded NutrientProfile."""
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


class PortionUnit(BaseModel):
    """Conventional unit of measurement for food portions."""
    model_config = ConfigDict(extra="ignore")

    unit_id: str = Field(..., description="Unique unit key (e.g. 'serving_spoon', 'medium_wrap')")
    unit_name: str = Field(..., description="Display name (e.g. 'Serving Spoon')")
    gram_weight: float = Field(..., gt=0.0, description="Reference mass in grams for 1 unit")
    description: str = Field("", description="Colloquial description or guidance")


class DishPortionConfig(BaseModel):
    """Portion configuration and available units for a dish."""
    model_config = ConfigDict(extra="ignore")

    dish_id: Optional[str] = None
    dish_name: Optional[str] = None
    default_unit_id: str = "standard_serving"
    default_quantity: float = 1.0
    units: List[PortionUnit] = Field(default_factory=list)


class PortionUnitsRegistry(BaseModel):
    """Registry of conventional portion units across dishes."""
    model_config = ConfigDict(extra="ignore")

    portion_units: Dict[str, DishPortionConfig] = Field(default_factory=dict)
    generic_default_units: Optional[DishPortionConfig] = None


class FoodItemFCT(BaseModel):
    """Individual food item record from Food Composition Table (per 100g raw)."""
    model_config = ConfigDict(extra="ignore")

    code: str
    food_name: str
    nutrients: NutrientProfile


class Ingredient(BaseModel):
    """Ingredient in a dish recipe."""
    model_config = ConfigDict(extra="ignore")

    ingredient_code: str
    name: str
    quantity_g: float = Field(..., ge=0.0)


class Recipe(BaseModel):
    """Recipe definition for a composite dish."""
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


class CompositeDish(BaseModel):
    """Compiled composite dish record stored in lookup and vector store."""
    model_config = ConfigDict(extra="ignore")

    dish_id: str
    dish_name: str
    standard_serving_g: float = 250.0
    cooking_yield_factor: float = 1.0
    raw_ingredients: List[Ingredient] = Field(default_factory=list)
    nutrients_raw_100g: Optional[NutrientProfile] = None
    nutrients_cooked_100g: NutrientProfile
    raw_batch_mass_g: float = 0.0
    wafct_code: str = "WAFCT_COMPOSITE"
    description: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)


class ScaledItemNutrition(BaseModel):
    """Itemized scaled dish nutrition matching canonical API schema."""
    model_config = ConfigDict(extra="ignore")

    item_id: Optional[str] = None
    dish_id: str
    display_name: str
    confidence: float = 1.0
    bounding_box: Optional[List[float]] = None
    weight_g: float
    wafct_code: str = "WAFCT_COMPOSITE"
    similarity_score: float = 1.0
    is_fallback: bool = False
    nutrients: NutrientProfile
    available_portion_units: List[PortionUnit] = Field(default_factory=list)
    default_unit_id: Optional[str] = None
    default_quantity: float = 1.0
    selected_unit_id: Optional[str] = None
    selected_quantity: Optional[float] = None
    nutrients_per_100g: Optional[NutrientProfile] = None


class TotalNutrition(BaseModel):
    """Total aggregated nutrition for a full meal."""
    model_config = ConfigDict(extra="ignore")

    total_calories_kcal: float = 0.0
    total_protein_g: float = 0.0
    total_fat_g: float = 0.0
    total_carbs_g: float = 0.0
    total_fiber_g: float = 0.0
    total_sodium_mg: float = 0.0
    total_calcium_mg: float = 0.0
    total_iron_mg: float = 0.0

    def round_values(self, decimals: int = 1) -> "TotalNutrition":
        """Return rounded TotalNutrition."""
        return TotalNutrition(
            total_calories_kcal=round(self.total_calories_kcal, decimals),
            total_protein_g=round(self.total_protein_g, decimals),
            total_fat_g=round(self.total_fat_g, decimals),
            total_carbs_g=round(self.total_carbs_g, decimals),
            total_fiber_g=round(self.total_fiber_g, decimals),
            total_sodium_mg=round(self.total_sodium_mg, decimals),
            calcium_mg=round(self.total_calcium_mg, decimals),
            total_calcium_mg=round(self.total_calcium_mg, decimals),
            total_iron_mg=round(self.total_iron_mg, decimals),
        )


class MealItemInput(BaseModel):
    """Input query payload for a detected food item."""
    model_config = ConfigDict(extra="ignore")

    dish_id: Optional[str] = None
    dish_name: Optional[str] = None
    query: Optional[str] = None
    weight_g: Optional[float] = None
    unit_id: Optional[str] = None
    quantity: Optional[float] = None
    custom_weight_g: Optional[float] = None
    item_id: Optional[str] = None
    confidence: float = 1.0
    bounding_box: Optional[List[float]] = None


class MealAnalysisResponse(BaseModel):
    """Full meal analysis response returned to backend/frontend."""
    model_config = ConfigDict(extra="ignore")

    analysis_id: str
    status: str = "success"
    processing_duration_ms: float
    image_url: Optional[str] = None
    detected_items: List[ScaledItemNutrition]
    total_nutrition: TotalNutrition
