"""Celery 配置与异步任务定义。"""

import logging

from celery import Celery

from app.core.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "baize",
    broker="redis://localhost:6379/0",     # 生产环境使用 Redis
    backend="redis://localhost:6379/0",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
)


@celery_app.task(bind=True, name="process_document")
def process_document_task(self, doc_id: str, kb_id: str, filename: str, content: bytes):
    """
    异步处理文档：解析 → 切块 → 向量化 → 存储。

    由文档上传接口触发，不阻塞 HTTP 响应。
    """
    from app.core.database import SessionLocal
    from app.models.document import Document
    from app.utils.parser import parse_document
    from app.utils.chunker import chunk_text
    from app.services.vector_store import vector_store

    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            logger.error("文档不存在: %s", doc_id)
            return

        # 更新状态
        doc.status = "processing"
        db.commit()

        # 1. 解析文档
        logger.info("开始处理文档: %s, %d bytes", filename, len(content))
        text = parse_document(filename, content)

        # 2. 文本切块
        chunks = chunk_text(text)

        # 3. 向量化 + 存储
        from app.services.chat_service import ChatService
        chat_service = ChatService()
        vectors = []
        for chunk in chunks:
            vec = chat_service._encode(chunk)
            vectors.append(vec[0])
        vectors_array = __import__("numpy").array(vectors)

        vector_store.insert(kb_id, doc_id, filename, chunks, vectors_array)

        # 4. 更新文档状态
        doc.status = "done"
        doc.chunk_count = len(chunks)
        db.commit()

        logger.info("文档处理完成: %s, 切块数=%d", filename, len(chunks))

    except Exception as e:
        logger.error("文档处理失败: %s, error=%s", filename, e)
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.status = "failed"
            db.commit()
        raise

    finally:
        db.close()
