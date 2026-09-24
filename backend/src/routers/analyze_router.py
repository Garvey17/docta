"""Meal Image Analysis Endpoint (CV Identification + Conventional Portion Units)."""

from typing import Optional
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    Request,
    status,
)

from ..schemas.analyze import AnalyzeMealResponse, AnalyzeImageURLRequest
from ..services.orchestrator_service import get_orchestrator_service, OrchestratorService

router = APIRouter(prefix="/api/v1", tags=["Analysis & Computer Vision"])


@router.post(
    "/analyze",
    response_model=AnalyzeMealResponse,
    status_code=status.HTTP_200_OK,
    summary="Identify food items in meal image and attach conventional portion units",
)
async def analyze_meal_endpoint(
    request: Request,
    orchestrator: OrchestratorService = Depends(get_orchestrator_service),
):
    """
    Multimodal meal analysis pipeline (<2.0s SLA):
    1. Invokes Computer Vision inference (Food Identification & Bounding Boxes only).
    2. Queries RAG / Portion Registry to attach available conventional units (spoons, wraps, slices).
    3. Attaches base 100g WAFCT nutritional profiles.
    4. Emits structured payload for user quantity confirmation on frontend.
    """
    content_type = request.headers.get("content-type", "")

    # 1. Handle multipart/form-data (File upload)
    if "multipart/form-data" in content_type:
        form = await request.form()
        file = form.get("file")
        prompt = form.get("prompt")
        prompt_str = str(prompt) if prompt is not None else None

        if file and hasattr(file, "filename") and file.filename:
            return await orchestrator.analyze_image_file(file=file, prompt=prompt_str)

    # 2. Handle application/json (Image URL / Base64 / Prompt)
    if "application/json" in content_type:
        body = await request.json()
        image_url = body.get("image_url")
        image_base64 = body.get("image_base64")
        prompt = body.get("prompt")
        return await orchestrator.analyze_image_url(
            image_url=image_url,
            image_base64=image_base64,
            prompt=prompt,
        )

    # Fallback default analysis
    return await orchestrator.analyze_image_url()
