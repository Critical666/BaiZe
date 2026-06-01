"""聊天相关路由。"""

from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.api.deps import get_chat_service

router = APIRouter()


@router.post("/knowledge-bases/{kb_id}/chat", response_model=ChatResponse)
def chat(
    kb_id: str,
    data: ChatRequest,
    service: ChatService = Depends(get_chat_service),
):
    """发起对话（阶段 A：占位回答，阶段 A2 接通 RAG）。"""
    return service.chat(kb_id, data)
