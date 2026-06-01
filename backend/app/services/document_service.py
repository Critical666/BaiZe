"""文档业务逻辑。"""

import uuid
import logging

from sqlalchemy.orm import Session

from app.models.document import Document

logger = logging.getLogger(__name__)


class DocumentService:
    """文档服务（阶段 A：仅存元数据，不做切块/向量化）。"""

    def __init__(self, db: Session):
        self.db = db

    def upload(self, kb_id: str, filename: str, file_size: int, user_id: str) -> Document:
        """上传文档，仅记录元数据。切块/向量化在阶段 A2 实现。"""
        doc = Document(
            id=str(uuid.uuid4()),
            kb_id=kb_id,
            filename=filename,
            file_size=file_size,
            status="pending",
            uploaded_by=user_id,
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        logger.info("文档上传: %s → kb=%s", filename, kb_id)
        return doc

    def list_by_kb(self, kb_id: str) -> list[Document]:
        """获取指定知识库的文档列表。"""
        return self.db.query(Document).filter(Document.kb_id == kb_id).order_by(
            Document.created_at.desc()
        ).all()
