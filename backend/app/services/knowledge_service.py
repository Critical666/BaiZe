"""知识库业务逻辑。"""

import uuid
import logging

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.knowledge_base import KnowledgeBase
from app.schemas.knowledge_base import KnowledgeBaseCreate

logger = logging.getLogger(__name__)


class KnowledgeService:
    """知识库服务。"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: KnowledgeBaseCreate, owner_id: str) -> dict:
        """创建知识库。"""
        kb = KnowledgeBase(
            id=str(uuid.uuid4()),
            name=data.name,
            description=data.description,
            owner_id=owner_id,
        )
        self.db.add(kb)
        self.db.commit()
        self.db.refresh(kb)
        logger.info("知识库创建: %s (owner=%s)", kb.name, owner_id)
        return {
            "id": kb.id,
            "name": kb.name,
            "description": kb.description,
            "owner_id": kb.owner_id,
            "created_at": str(kb.created_at),
            "updated_at": str(kb.updated_at),
        }

    def list_all(self, offset: int = 0, limit: int = 20) -> list[dict]:
        """获取知识库列表（分页）。"""
        kbs = self.db.query(KnowledgeBase).order_by(
            KnowledgeBase.created_at.desc()
        ).offset(offset).limit(limit).all()
        return [
            {
                "id": kb.id,
                "name": kb.name,
                "description": kb.description,
                "owner_id": kb.owner_id,
                "created_at": str(kb.created_at),
                "updated_at": str(kb.updated_at),
            }
            for kb in kbs
        ]

    def get_detail(self, kb_id: str) -> dict:
        """获取知识库详情，含文档数量。"""
        kb = self.db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
        if not kb:
            raise ValueError(f"知识库 {kb_id} 不存在")

        doc_count = self.db.query(Document).filter(Document.kb_id == kb_id).count()
        return {
            "id": kb.id,
            "name": kb.name,
            "description": kb.description,
            "owner_id": kb.owner_id,
            "created_at": str(kb.created_at),
            "updated_at": str(kb.updated_at),
            "document_count": doc_count,
        }

    def delete(self, kb_id: str) -> bool:
        """删除知识库及其关联文档。"""
        kb = self.db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
        if not kb:
            raise ValueError(f"知识库 {kb_id} 不存在")

        self.db.query(Document).filter(Document.kb_id == kb_id).delete()
        self.db.delete(kb)
        self.db.commit()
        logger.info("知识库删除: %s", kb.name)
        return True
