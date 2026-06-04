"""聊天相关数据模型。"""

from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """聊天提问请求。"""

    question: str = Field(..., min_length=1, max_length=4096)
    top_k: int = Field(default=5, ge=1, le=20)
    new_chat: bool = Field(default=False, description="是否开启新对话（忽略历史上下文）")


class ChatResponse(BaseModel):
    """聊天回答响应。"""

    answer: str
    sources: List[str] = []


class ChatHistoryResponse(BaseModel):
    """聊天历史记录响应。"""

    id: str
    kb_id: str
    user_id: str
    question: str
    answer: str
    sources: List[str] = []
    created_at: str
