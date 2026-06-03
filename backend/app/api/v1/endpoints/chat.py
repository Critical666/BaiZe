"""聊天相关路由。"""

from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.api.deps import get_chat_service, get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/knowledge-bases/{kb_id}/chat", response_model=ChatResponse)
def chat(
    kb_id: str,
    data: ChatRequest,
    service: ChatService = Depends(get_chat_service),
    current_user: User = Depends(get_current_user),
):
    """发起对话（需登录）。"""
    return service.chat(kb_id, data, user_id=current_user.id)
