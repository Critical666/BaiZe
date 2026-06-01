"""文档相关路由。"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.services.document_service import DocumentService
from app.models.user import User
from app.api.deps import get_document_service, get_current_user

router = APIRouter()


@router.post("/knowledge-bases/{kb_id}/documents")
def upload_doc(
    kb_id: str,
    file: UploadFile = File(...),
    service: DocumentService = Depends(get_document_service),
    current_user: User = Depends(get_current_user),
):
    """上传文档（阶段 A：仅存元数据，不做切块/向量化）。"""
    content = file.file.read()
    return service.upload(kb_id, file.filename, len(content), current_user.id)


@router.get("/knowledge-bases/{kb_id}/documents")
def list_docs(
    kb_id: str,
    service: DocumentService = Depends(get_document_service),
):
    """获取文档列表。"""
    return service.list_by_kb(kb_id)
