"""Insight Chatbot Request and Response Pydantic Schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    role: str = Field(..., description="Role of the sender ('user' or 'assistant')")
    content: str = Field(..., description="Content text of the message")


class InsightChatRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    message: str = Field(..., min_length=1, description="User's query for the nutritionist chatbot")
    history: Optional[List[ChatMessage]] = Field(
        default_factory=list,
        description="Prior conversation history between user and nutritionist",
    )


class InsightChatResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    reply: str = Field(..., description="Nutritionist's response text")
    status: str = Field(default="success", description="Status code or flag")
