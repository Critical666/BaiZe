"""统计业务逻辑。"""

import logging

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.document import Document
from app.models.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)


class StatsService:
    """统计服务。"""

    def __init__(self, db: Session):
        self.db = db

    def get_overview(self) -> dict:
        """获取全量统计概览。"""
        kb_count = self.db.query(func.count(KnowledgeBase.id)).scalar()
        doc_count = self.db.query(func.count(Document.id)).scalar()
        chunk_count = self.db.query(func.sum(Document.chunk_count)).scalar() or 0

        # 从聊天记录表查询近7天对话数
        chat_count_7d = self._get_chat_count_7d()

        return {
            "knowledge_base_count": kb_count,
            "document_count": doc_count,
            "chunk_count": chunk_count,
            "chat_count_7d": chat_count_7d,
        }

    def _get_chat_count_7d(self) -> int:
        """查询近 7 天的聊天记录数。"""
        try:
            from app.services.chat_history_service import ChatHistoryService

            return ChatHistoryService(self.db).count_recent(7)
        except Exception as e:
            logger.warning("查询聊天记录数失败，返回 0: %s", e)
            return 0
