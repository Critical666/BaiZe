"""知识库相关路由。"""

from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.knowledge_base import KnowledgeBaseCreate
from app.services.knowledge_service import KnowledgeService
from app.api.deps import get_knowledge_service, get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/knowledge-bases")
def create_kb(
    data: KnowledgeBaseCreate,
    service: KnowledgeService = Depends(get_knowledge_service),
    current_user: User = Depends(get_current_user),
):
    """创建知识库（权限装饰器暂不生效，阶段 3 挂载）。"""
    return service.create(data, current_user.id)


@router.get("/knowledge-bases")
def list_kb(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """获取知识库列表（分页）。"""
    return service.list_all(offset, limit)


@router.get("/knowledge-bases/{kb_id}")
def get_kb(
    kb_id: str,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """获取知识库详情。"""
    try:
        return service.get_detail(kb_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/knowledge-bases/{kb_id}")
def delete_kb(
    kb_id: str,
    service: KnowledgeService = Depends(get_knowledge_service),
    current_user: User = Depends(get_current_user),
):
    """删除知识库（权限装饰器暂不生效，阶段 3 挂载）。"""
    try:
        return {"deleted": service.delete(kb_id)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
