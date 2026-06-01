"""聊天相关数据模型。"""

from typing import List

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """聊天提问请求。"""

    question: str = Field(..., min_length=1, max_length=4096)
    top_k: int = Field(default=5, ge=1, le=20)


class ChatResponse(BaseModel):
    """聊天回答响应。"""

    answer: str
    sources: List[str] = []
