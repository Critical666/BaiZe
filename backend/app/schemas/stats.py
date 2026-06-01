"""统计相关数据模型。"""

from pydantic import BaseModel


class StatsResponse(BaseModel):
    """统计概览响应。"""

    knowledge_base_count: int
    document_count: int
    chunk_count: int
    chat_count_7d: int = 0
