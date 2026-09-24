"""Active Learning Telemetry Service for decision logging and ML export."""

import io
import csv
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.meal_item_feedback_log import MealItemFeedbackLog
from ..schemas.meal import LogMealItemInput
from ..schemas.telemetry import TelemetryStatsResponse


class TelemetryService:
    """Manages telemetry logging and dataset exports for the ML team."""

    @staticmethod
    async def log_item_decision(
        db: AsyncSession,
        user_id: Optional[uuid.UUID],
        meal_id: uuid.UUID,
        item: LogMealItemInput,
        saved_meal_item_id: Optional[uuid.UUID] = None,
        image_url: Optional[str] = None,
    ) -> MealItemFeedbackLog:
        """Persist decision log for an individual meal item."""
        entry = MealItemFeedbackLog(
            id=uuid.uuid4(),
            user_id=user_id,
            meal_id=meal_id,
            meal_item_id=saved_meal_item_id,
            image_url=image_url,
            predicted_dish_id=item.predicted_dish_id,
            predicted_confidence=item.confidence,
            bounding_box=item.bounding_box,
            final_dish_id=item.final_dish_id,
            label_modified=bool(item.label_modified or (item.predicted_dish_id != item.final_dish_id)),
            selected_unit_id=item.selected_unit_id,
            selected_quantity=item.selected_quantity,
            calculated_gram_weight=item.gram_weight,
            custom_weight_entered_g=item.custom_weight_entered_g,
            logged_at=datetime.now(timezone.utc),
        )
        db.add(entry)
        return entry

    @staticmethod
    async def export_records(
        db: AsyncSession,
        dish_id: Optional[str] = None,
        label_modified_only: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> Tuple[List[MealItemFeedbackLog], int]:
        """Query decision logs with optional filters."""
        q = select(MealItemFeedbackLog)
        cq = select(func.count(MealItemFeedbackLog.id))

        if dish_id:
            cond = (MealItemFeedbackLog.predicted_dish_id == dish_id) | (MealItemFeedbackLog.final_dish_id == dish_id)
            q, cq = q.where(cond), cq.where(cond)
        if label_modified_only is not None:
            q, cq = q.where(MealItemFeedbackLog.label_modified == label_modified_only), cq.where(MealItemFeedbackLog.label_modified == label_modified_only)
        if start_date:
            q, cq = q.where(MealItemFeedbackLog.logged_at >= start_date), cq.where(MealItemFeedbackLog.logged_at >= start_date)
        if end_date:
            q, cq = q.where(MealItemFeedbackLog.logged_at <= end_date), cq.where(MealItemFeedbackLog.logged_at <= end_date)

        total = (await db.execute(cq)).scalar() or 0
        records = (await db.execute(q.order_by(desc(MealItemFeedbackLog.logged_at)).offset(offset).limit(limit))).scalars().all()
        return list(records), total

    @staticmethod
    def records_to_csv(records: List[MealItemFeedbackLog]) -> str:
        """Serialize telemetry records to CSV."""
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow([
            "id", "user_id", "meal_id", "image_url", "predicted_dish_id",
            "predicted_confidence", "bounding_box", "final_dish_id", "label_modified",
            "selected_unit_id", "selected_quantity", "calculated_gram_weight",
            "custom_weight_entered_g", "logged_at"
        ])
        for r in records:
            w.writerow([
                str(r.id), str(r.user_id or ""), str(r.meal_id or ""), r.image_url or "",
                r.predicted_dish_id, r.predicted_confidence, str(r.bounding_box or ""),
                r.final_dish_id, r.label_modified, r.selected_unit_id, r.selected_quantity,
                r.calculated_gram_weight, r.custom_weight_entered_g or "",
                r.logged_at.isoformat() if r.logged_at else ""
            ])
        return buf.getvalue()

    @staticmethod
    async def get_stats(db: AsyncSession) -> TelemetryStatsResponse:
        """Compute summary statistics."""
        total = (await db.execute(select(func.count(MealItemFeedbackLog.id)))).scalar() or 0
        mods = (await db.execute(select(func.count(MealItemFeedbackLog.id)).where(MealItemFeedbackLog.label_modified.is_(True)))).scalar() or 0

        # Helper for top group counts
        async def top_counts(column):
            res = await db.execute(
                select(column, func.count(MealItemFeedbackLog.id))
                .group_by(column).order_by(desc(func.count(MealItemFeedbackLog.id))).limit(10)
            )
            return {r[0]: r[1] for r in res.all()}

        return TelemetryStatsResponse(
            total_decisions_logged=total,
            total_label_modifications=mods,
            modification_rate=round(mods / total, 4) if total > 0 else 0.0,
            top_predicted_dishes=await top_counts(MealItemFeedbackLog.predicted_dish_id),
            top_final_dishes=await top_counts(MealItemFeedbackLog.final_dish_id),
            top_portion_units=await top_counts(MealItemFeedbackLog.selected_unit_id),
        )
