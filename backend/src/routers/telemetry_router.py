"""Telemetry and Active Learning Export API Endpoints (ML Team Interface)."""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.telemetry import TelemetryExportResponse, TelemetryStatsResponse, TelemetryRecord
from ..services.telemetry_service import TelemetryService

router = APIRouter(prefix="/api/v1/telemetry", tags=["Telemetry & ML Active Learning"])


@router.get(
    "/export",
    summary="Export active learning dataset for training future portion-size models",
    response_model=Optional[TelemetryExportResponse],
)
async def export_telemetry(
    format: str = Query("json", description="Export format: 'json' or 'csv'"),
    dish_id: Optional[str] = Query(None, description="Filter by dish ID"),
    modified_only: Optional[bool] = Query(None, description="Filter only user-corrected predictions"),
    start_date: Optional[datetime] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date filter (ISO format)"),
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    ML/CV Team Data Bridge:
    Exports granular user decisions (predicted vs final dish, chosen portion unit, quantity, gram weight)
    to facilitate retraining computer vision classification and training automated portion-weight estimation models.
    """
    records, total_count = await TelemetryService.export_records(
        db=db,
        dish_id=dish_id,
        label_modified_only=modified_only,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )

    if format.lower() == "csv":
        csv_data = TelemetryService.records_to_csv(records)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=docta_telemetry_export.csv"},
        )

    # Return standard JSON format
    return TelemetryExportResponse(
        total_records=total_count,
        exported_at=datetime.now(timezone.utc),
        records=[TelemetryRecord.model_validate(r) for r in records],
    )


@router.get(
    "/stats",
    response_model=TelemetryStatsResponse,
    summary="Get aggregated statistics on user decisions and corrections",
)
async def get_telemetry_statistics(
    db: AsyncSession = Depends(get_db),
):
    """Returns analytics on prediction accuracy, label modifications, and top portion units."""
    return await TelemetryService.get_stats(db=db)
