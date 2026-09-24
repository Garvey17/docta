"""SQLAlchemy Meal Model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, Uuid
from sqlalchemy.orm import relationship

from ..database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = Column(String(1024), nullable=True)
    meal_type = Column(String(50), nullable=False, default="lunch")  # breakfast, lunch, dinner, snack
    notes = Column(Text, nullable=True)
    logged_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    # Aggregated Nutritional Totals
    total_calories_kcal = Column(Float, default=0.0, nullable=False)
    total_protein_g = Column(Float, default=0.0, nullable=False)
    total_fat_g = Column(Float, default=0.0, nullable=False)
    total_carbs_g = Column(Float, default=0.0, nullable=False)
    total_fiber_g = Column(Float, default=0.0, nullable=False)
    total_sodium_mg = Column(Float, default=0.0, nullable=False)
    total_calcium_mg = Column(Float, default=0.0, nullable=False)
    total_iron_mg = Column(Float, default=0.0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="meals")
    items = relationship("MealItem", back_populates="meal", cascade="all, delete-orphan")
    feedback_logs = relationship("MealItemFeedbackLog", back_populates="meal", cascade="all, delete-orphan")
