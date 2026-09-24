"""SQLAlchemy MealItemFeedbackLog Model.

Active learning telemetry database table storing granular food identification
predictions, user corrections, selected conventional portion units, and calculated
weights for future model training and dataset exports.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, JSON, Uuid
from sqlalchemy.orm import relationship

from ..database import Base


def utcnow():
    return datetime.now(timezone.utc)


class MealItemFeedbackLog(Base):
    __tablename__ = "meal_item_feedback_logs"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    meal_id = Column(Uuid(as_uuid=True), ForeignKey("meals.id", ondelete="CASCADE"), nullable=True, index=True)
    meal_item_id = Column(Uuid(as_uuid=True), ForeignKey("meal_items.id", ondelete="CASCADE"), nullable=True)

    image_url = Column(String(1024), nullable=True)
    predicted_dish_id = Column(String(100), nullable=False, index=True)
    predicted_confidence = Column(Float, nullable=False, default=1.0)
    bounding_box = Column(JSON, nullable=True)  # [x_min, y_min, x_max, y_max]

    final_dish_id = Column(String(100), nullable=False, index=True)
    label_modified = Column(Boolean, nullable=False, default=False, index=True)

    selected_unit_id = Column(String(100), nullable=False)
    selected_quantity = Column(Float, nullable=False, default=1.0)
    calculated_gram_weight = Column(Float, nullable=False)
    custom_weight_entered_g = Column(Float, nullable=True)

    logged_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="feedback_logs")
    meal = relationship("Meal", back_populates="feedback_logs")
