"""文档相关数据模型。"""

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    """文档上传成功响应。"""

    id: str
    kb_id: str
    filename: str
    status: str = "pending"


class DocumentResponse(BaseModel):
    """文档列表响应。"""

    id: str
    kb_id: str
    filename: str
    file_size: int
    chunk_count: int
    status: str  # pending | processing | done | failed
    created_at: str
