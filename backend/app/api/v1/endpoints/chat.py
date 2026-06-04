"""聊天相关路由。"""

from fastapi import APIRouter, Depends, Query
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse
from app.services.chat_service import ChatService
from app.services.chat_history_service import ChatHistoryService
from app.api.deps import get_chat_service, get_chat_history_service, get_current_user
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


@router.get(
    "/knowledge-bases/{kb_id}/chat-history",
    response_model=list[ChatHistoryResponse],
)
def list_chat_history(
    kb_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: ChatHistoryService = Depends(get_chat_history_service),
    _current_user: User = Depends(get_current_user),
):
    """获取指定知识库的聊天历史记录（分页，需登录）。"""
    return service.list_by_kb(kb_id, offset=offset, limit=limit)
