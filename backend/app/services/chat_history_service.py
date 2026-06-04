"""聊天记录服务。"""

import json
import logging
import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.chat_history import ChatHistory

logger = logging.getLogger(__name__)


class ChatHistoryService:
    """聊天记录业务逻辑。"""

    def __init__(self, db: Session):
        self.db = db

    def save_chat(
        self,
        kb_id: str,
        user_id: str,
        question: str,
        answer: str,
        sources: list[str],
    ) -> ChatHistory:
        """
        保存一条聊天记录。

        Args:
            kb_id: 知识库 ID。
            user_id: 用户 ID。
            question: 用户问题。
            answer: 助手回答。
            sources: 来源引用列表。

        Returns:
            创建的 ChatHistory 对象。
        """
        record = ChatHistory(
            id=str(uuid.uuid4()),
            kb_id=kb_id,
            user_id=user_id,
            question=question,
            answer=answer,
            sources=json.dumps(sources, ensure_ascii=False),
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        logger.info("聊天记录已保存: kb=%s, user=%s", kb_id, user_id)
        return record

    def list_by_kb(self, kb_id: str, offset: int = 0, limit: int = 50) -> list[dict]:
        """
        获取指定知识库的聊天历史（分页）。

        Args:
            kb_id: 知识库 ID。
            offset: 分页偏移量。
            limit: 每页条数。

        Returns:
            聊天历史列表，按时间倒序。
        """
        records = (
            self.db.query(ChatHistory)
            .filter(ChatHistory.kb_id == kb_id)
            .order_by(ChatHistory.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "kb_id": r.kb_id,
                "user_id": r.user_id,
                "question": r.question,
                "answer": r.answer,
                "sources": json.loads(r.sources) if r.sources else [],
                "created_at": str(r.created_at),
            }
            for r in records
        ]

    def count_recent(self, days: int = 7) -> int:
        """
        统计最近 N 天的聊天次数。

        Args:
            days: 统计天数，默认 7 天。

        Returns:
            聊天记录数量。
        """
        since = datetime.utcnow() - timedelta(days=days)
        count = (
            self.db.query(func.count(ChatHistory.id))
            .filter(ChatHistory.created_at >= since)
            .scalar()
        )
        return count or 0
