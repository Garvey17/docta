"""Insight Chatbot Router providing Agentic RAG nutrition insights."""

from typing import Optional
from fastapi import APIRouter, Depends, status

from ..dependencies.auth import get_current_user_optional
from ..schemas.auth import UserResponse
from ..schemas.insight import InsightChatRequest, InsightChatResponse
from ..services.insight_service import InsightService

DEFAULT_DEMO_USER_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479"

router = APIRouter(prefix="/api/v1/insights", tags=["Insights & Nutritionist Chatbot"])


@router.post(
    "/chat",
    response_model=InsightChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with the AI Nutritionist (Agentic RAG over user meals & history)",
)
async def chat_with_nutritionist(
    payload: InsightChatRequest,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """
    Chat with the Agentic Nutritionist AI.
    - Restricted strictly to clinical nutrition and dietary guidance.
    - Dynamically queries database tools for the current user's logged meals and nutrition targets.
    - Uses retrieved data as context (RAG) to produce personalized insights.
    """
    user_id = current_user.id if current_user else DEFAULT_DEMO_USER_ID

    reply = await InsightService.chat(
        user_id=user_id,
        message=payload.message,
        history=payload.history,
    )

    return InsightChatResponse(reply=reply, status="success")
