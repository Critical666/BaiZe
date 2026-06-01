"""文档相关路由。"""

from fastapi import APIRouter, Depends, UploadFile, File
from app.services.document_service import DocumentService
from app.models.user import User
from app.api.deps import get_document_service, get_current_user

router = APIRouter()


@router.post("/knowledge-bases/{kb_id}/documents")
async def upload_doc(
    kb_id: str,
    file: UploadFile = File(...),
    service: DocumentService = Depends(get_document_service),
    current_user: User = Depends(get_current_user),
):
    """上传文档并触发异步处理。"""
    content = await file.read()
    return service.upload(kb_id, file.filename, len(content), content, current_user.id)


@router.get("/knowledge-bases/{kb_id}/documents")
def list_docs(
    kb_id: str,
    service: DocumentService = Depends(get_document_service),
):
    """获取文档列表。"""
    return service.list_by_kb(kb_id)
