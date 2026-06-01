"""文档业务逻辑。"""

import uuid
import logging

from sqlalchemy.orm import Session

from app.models.document import Document

logger = logging.getLogger(__name__)


class DocumentService:
    """文档服务。"""

    def __init__(self, db: Session):
        self.db = db

    def upload(
        self,
        kb_id: str,
        filename: str,
        file_size: int,
        content: bytes,
        user_id: str,
    ) -> Document:
        """上传文档并触发异步处理。"""
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

        # 异步处理（开发模式：同步执行）
        self._process_async(doc.id, kb_id, filename, content)

        return doc

    def list_by_kb(self, kb_id: str) -> list[Document]:
        """获取指定知识库的文档列表。"""
        return (
            self.db.query(Document)
            .filter(Document.kb_id == kb_id)
            .order_by(Document.created_at.desc())
            .all()
        )

    def _process_async(self, doc_id: str, kb_id: str, filename: str, content: bytes):
        """处理文档（开发模式：内联同步；生产模式：Celery 异步）。"""
        # TODO: Celery Worker 就绪后改为 process_document_task.delay(...)
        self._process_inline(doc_id, kb_id, filename, content)

    def _process_inline(self, doc_id: str, kb_id: str, filename: str, content: bytes):
        """内联同步处理文档（Celery 不可用时的降级方案）。"""
        from app.utils.parser import parse_document
        from app.utils.chunker import chunk_text
        from app.services.vector_store import vector_store

        doc = self.db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return

        try:
            doc.status = "processing"
            self.db.commit()

            # 1. 解析
            text = parse_document(filename, content)
            # 2. 切块
            chunks = chunk_text(text)
            # 3. 向量化
            from app.services.chat_service import ChatService
            import numpy as np

            cs = ChatService()
            vectors = np.array([cs._encode(c)[0] for c in chunks])
            # 4. 存储
            vector_store.insert(kb_id, doc_id, filename, chunks, vectors)

            doc.status = "done"
            doc.chunk_count = len(chunks)
            self.db.commit()
            logger.info("文档处理完成: %s, 切块=%d", filename, len(chunks))
        except Exception as e:
            import traceback
            logger.error("文档处理失败: %s, error=%s", filename, e)
            logger.error(traceback.format_exc())
            doc.status = "failed"
            self.db.commit()
