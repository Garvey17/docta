"""SQLAlchemy MealItem Model."""

import uuid
from sqlalchemy import Column, String, Float, Boolean, ForeignKey, JSON, Uuid
from sqlalchemy.orm import relationship

from ..database import Base


class MealItem(Base):
    __tablename__ = "meal_items"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    meal_id = Column(Uuid(as_uuid=True), ForeignKey("meals.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(String(100), nullable=True)  # client-assigned ephemeral ID e.g., "item_1"
    food_name = Column(String(255), nullable=False)
    predicted_dish_id = Column(String(100), nullable=False)
    final_dish_id = Column(String(100), nullable=False)
    label_modified = Column(Boolean, default=False, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    bounding_box = Column(JSON, nullable=True)  # [x_min, y_min, x_max, y_max]

    # Selected Portion Units
    selected_unit_id = Column(String(100), nullable=True)
    selected_quantity = Column(Float, default=1.0, nullable=True)
    gram_weight = Column(Float, default=100.0, nullable=False)

    # Scaled Nutritional Values
    calories_kcal = Column(Float, default=0.0, nullable=False)
    protein_g = Column(Float, default=0.0, nullable=False)
    fat_g = Column(Float, default=0.0, nullable=False)
    carbs_g = Column(Float, default=0.0, nullable=False)
    fiber_g = Column(Float, default=0.0, nullable=False)
    sodium_mg = Column(Float, default=0.0, nullable=False)
    calcium_mg = Column(Float, default=0.0, nullable=False)
    iron_mg = Column(Float, default=0.0, nullable=False)

    # Relationships
    meal = relationship("Meal", back_populates="items")
