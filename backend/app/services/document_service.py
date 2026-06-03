"""文档业务逻辑。"""

import os
import uuid
import logging

from sqlalchemy.orm import Session

from app.models.document import Document
from app.core.config import settings

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
    ) -> dict:
        """上传文档，落盘保存，触发异步处理。"""
        doc_id = str(uuid.uuid4())

        # 落盘保存文件
        file_dir = os.path.join(settings.upload_dir, doc_id)
        os.makedirs(file_dir, exist_ok=True)
        file_path = os.path.join(file_dir, filename)
        with open(file_path, "wb") as f:
            f.write(content)
        logger.info("文件落盘: %s → %s", filename, file_path)

        doc = Document(
            id=doc_id,
            kb_id=kb_id,
            filename=filename,
            file_size=file_size,
            file_path=file_path,
            status="pending",
            uploaded_by=user_id,
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        logger.info("文档记录创建: %s → kb=%s", filename, kb_id)

        # 异步处理（只传 doc_id，不传 bytes）
        self._process_async(doc_id)

        return self._doc_to_dict(doc)

    def list_by_kb(self, kb_id: str) -> list[dict]:
        """获取指定知识库的文档列表。"""
        docs = (
            self.db.query(Document)
            .filter(Document.kb_id == kb_id)
            .order_by(Document.created_at.desc())
            .all()
        )
        return [self._doc_to_dict(d) for d in docs]

    @staticmethod
    def _doc_to_dict(doc: Document) -> dict:
        """ORM 对象转字典（确保 datetime → str）。"""
        return {
            "id": doc.id,
            "kb_id": doc.kb_id,
            "filename": doc.filename,
            "file_size": doc.file_size,
            "chunk_count": doc.chunk_count,
            "status": doc.status,
            "created_at": str(doc.created_at),
            "uploaded_by": doc.uploaded_by,
        }

    def _process_async(self, doc_id: str):
        """根据配置选择 Celery 异步或后台线程处理。"""
        if settings.use_celery:
            try:
                from app.core.celery_app import process_document_task

                process_document_task.delay(doc_id)
                logger.info("文档已提交到 Celery: %s", doc_id)
                return
            except Exception as e:
                logger.warning("Celery 提交失败，降级后台线程: %s", e)

        # 后台线程处理，不阻塞 HTTP 响应
        import threading

        threading.Thread(
            target=self._process_in_thread,
            args=(doc_id,),
            daemon=True,
        ).start()
        logger.info("文档已提交后台线程处理: %s", doc_id)

    @staticmethod
    def _process_in_thread(doc_id: str):
        """后台线程处理文档（使用独立 DB 会话，线程安全）。"""
        from app.core.database import SessionLocal
        from app.utils.parser import parse_document
        from app.utils.chunker import chunk_text
        from app.services.vector_store import VectorStore
        from app.services.embedding_service import encode_texts

        db = SessionLocal()
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if not doc:
                logger.error("文档不存在: %s", doc_id)
                return

            try:
                doc.status = "processing"
                db.commit()

                # 从磁盘读取文件内容
                if not doc.file_path or not os.path.exists(doc.file_path):
                    raise FileNotFoundError(f"文件不存在: {doc.file_path}")
                with open(doc.file_path, "rb") as f:
                    content = f.read()

                # 1. 解析
                text = parse_document(doc.filename, content)
                logger.info("文档解析完成: %s, %d 字符", doc.filename, len(text))
                # 2. 切块
                chunks = chunk_text(text)
                logger.info("文档切块完成: %s, %d 块", doc.filename, len(chunks))
                # 3. 向量化
                vectors = encode_texts(chunks)
                logger.info("文档向量化完成: %s, shape=%s", doc.filename, vectors.shape)
                # 4. 存储（新建独立 VectorStore 实例，避免跨线程共享）
                vs = VectorStore()
                vs.insert(doc.kb_id, doc_id, doc.filename, chunks, vectors)

                doc.status = "done"
                doc.chunk_count = len(chunks)
                db.commit()
                logger.info("文档处理完成: %s, 切块=%d", doc.filename, len(chunks))
            except Exception as e:
                import traceback

                logger.error("文档处理失败: %s, error=%s", doc.filename, e)
                logger.error(traceback.format_exc())
                doc = db.query(Document).filter(Document.id == doc_id).first()
                if doc:
                    doc.status = "failed"
                    db.commit()
        finally:
            db.close()
