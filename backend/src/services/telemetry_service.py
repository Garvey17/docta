"""Active Learning Telemetry Service for decision logging and ML export."""

import io
import csv
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any, Union

from ..supabase_client import get_supabase_client
from ..schemas.meal import LogMealItemInput
from ..schemas.telemetry import TelemetryRecord, TelemetryStatsResponse

logger = logging.getLogger(__name__)


class TelemetryService:
    """Manages 'Log Everything' telemetry persistence and dataset exports for ML."""

    @staticmethod
    async def log_item_decision(
        user_id: Optional[str],
        meal_id: str,
        item: LogMealItemInput,
        saved_meal_item_id: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Persist granular user decision into meal_item_feedback_logs."""
        supabase = get_supabase_client()
        entry_id = str(uuid.uuid4())
        label_modified = bool(item.label_modified or (item.predicted_dish_id != item.final_dish_id))

        log_data = {
            "id": entry_id,
            "user_id": str(user_id) if user_id else None,
            "meal_id": str(meal_id),
            "meal_item_id": str(saved_meal_item_id) if saved_meal_item_id else None,
            "image_url": image_url,
            "predicted_dish_id": item.predicted_dish_id,
            "predicted_confidence": float(item.confidence),
            "bounding_box": item.bounding_box,
            "final_dish_id": item.final_dish_id,
            "label_modified": label_modified,
            "selected_unit_id": item.selected_unit_id,
            "selected_quantity": float(item.selected_quantity),
            "calculated_gram_weight": float(item.gram_weight),
            "custom_weight_entered_g": float(item.custom_weight_entered_g) if item.custom_weight_entered_g is not None else None,
            "logged_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            supabase.from_("meal_item_feedback_logs").insert(log_data).execute()
        except Exception as e:
            logger.error("Failed persisting telemetry log: %s", e)
            raise e

        return log_data

    @staticmethod
    async def export_records(
        dish_id: Optional[str] = None,
        label_modified_only: Optional[bool] = None,
        start_date: Optional[Union[datetime, str]] = None,
        end_date: Optional[Union[datetime, str]] = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Query decision logs with optional filters."""
        supabase = get_supabase_client()
        query = supabase.from_("meal_item_feedback_logs").select("*", count="exact")

        if dish_id:
            query = query.or_(f"predicted_dish_id.eq.{dish_id},final_dish_id.eq.{dish_id}")
        if label_modified_only is not None:
            query = query.eq("label_modified", label_modified_only)
        if start_date:
            s_val = start_date.isoformat() if hasattr(start_date, "isoformat") else str(start_date)
            query = query.gte("logged_at", s_val)
        if end_date:
            e_val = end_date.isoformat() if hasattr(end_date, "isoformat") else str(end_date)
            query = query.lte("logged_at", e_val)

        res = query.order("logged_at", desc=True).range(offset, offset + limit - 1).execute()
        records = res.data or []
        total_count = res.count if res.count is not None else len(records)
        return records, total_count

    @staticmethod
    def records_to_csv(records: List[Dict[str, Any]]) -> str:
        """Serialize telemetry records to CSV."""
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow([
            "id", "user_id", "meal_id", "meal_item_id", "image_url", "predicted_dish_id",
            "predicted_confidence", "bounding_box", "final_dish_id", "label_modified",
            "selected_unit_id", "selected_quantity", "calculated_gram_weight",
            "custom_weight_entered_g", "logged_at"
        ])
        for r in records:
            w.writerow([
                str(r.get("id", "")),
                str(r.get("user_id") or ""),
                str(r.get("meal_id") or ""),
                str(r.get("meal_item_id") or ""),
                r.get("image_url") or "",
                r.get("predicted_dish_id", ""),
                r.get("predicted_confidence", 1.0),
                str(r.get("bounding_box") or ""),
                r.get("final_dish_id", ""),
                r.get("label_modified", False),
                r.get("selected_unit_id", ""),
                r.get("selected_quantity", 1.0),
                r.get("calculated_gram_weight", 0.0),
                r.get("custom_weight_entered_g") or "",
                str(r.get("logged_at", "")),
            ])
        return buf.getvalue()

    @staticmethod
    async def get_stats() -> TelemetryStatsResponse:
        """Compute summary telemetry analytics."""
        supabase = get_supabase_client()
        res = supabase.from_("meal_item_feedback_logs").select("*").execute()
        records = res.data or []

        total = len(records)
        mods = sum(1 for r in records if r.get("label_modified") is True)

        top_pred: Dict[str, int] = {}
        top_final: Dict[str, int] = {}
        top_units: Dict[str, int] = {}

        for r in records:
            p_dish = r.get("predicted_dish_id")
            f_dish = r.get("final_dish_id")
            u_id = r.get("selected_unit_id")
            if p_dish:
                top_pred[p_dish] = top_pred.get(p_dish, 0) + 1
            if f_dish:
                top_final[f_dish] = top_final.get(f_dish, 0) + 1
            if u_id:
                top_units[u_id] = top_units.get(u_id, 0) + 1

        return TelemetryStatsResponse(
            total_decisions_logged=total,
            total_label_modifications=mods,
            modification_rate=round(mods / total, 4) if total > 0 else 0.0,
            top_predicted_dishes=dict(sorted(top_pred.items(), key=lambda x: x[1], reverse=True)[:10]),
            top_final_dishes=dict(sorted(top_final.items(), key=lambda x: x[1], reverse=True)[:10]),
            top_portion_units=dict(sorted(top_units.items(), key=lambda x: x[1], reverse=True)[:10]),
        )
