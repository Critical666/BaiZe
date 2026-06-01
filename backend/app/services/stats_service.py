"""统计业务逻辑。"""

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.document import Document
from app.models.knowledge_base import KnowledgeBase


class StatsService:
    """统计服务。"""

    def __init__(self, db: Session):
        self.db = db

    def get_overview(self) -> dict:
        """获取全量统计概览。"""
        kb_count = self.db.query(func.count(KnowledgeBase.id)).scalar()
        doc_count = self.db.query(func.count(Document.id)).scalar()
        chunk_count = self.db.query(func.sum(Document.chunk_count)).scalar() or 0

        return {
            "knowledge_base_count": kb_count,
            "document_count": doc_count,
            "chunk_count": chunk_count,
            "chat_count_7d": 0,  # 阶段 A2 中补充聊天记录统计
        }
