"""知识库相关数据模型。"""

from typing import Optional

from pydantic import BaseModel, Field


class KnowledgeBaseCreate(BaseModel):
    """知识库创建请求。"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class KnowledgeBaseResponse(BaseModel):
    """知识库列表响应。"""

    id: str
    name: str
    description: Optional[str] = None
    owner_id: str
    created_at: str
    updated_at: str


class KnowledgeBaseDetail(KnowledgeBaseResponse):
    """知识库详情（含文档数量）。"""

    document_count: int = 0
