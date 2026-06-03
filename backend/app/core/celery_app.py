"""Celery 配置与异步任务定义。"""

import logging

from celery import Celery

from app.core.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "baize",
    broker=settings.redis_url,
    backend=settings.redis_url,
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
def process_document_task(self, doc_id: str):
    """
    异步处理文档：从磁盘读取文件 → 解析 → 切块 → 向量化 → 写入 Milvus。

    仅接收 doc_id（字符串），从数据库获取文档信息，从磁盘读取文件内容。
    """
    import os

    from app.core.database import SessionLocal
    from app.models.document import Document
    from app.utils.parser import parse_document
    from app.utils.chunker import chunk_text
    from app.services.vector_store import vector_store
    from app.services.embedding_service import encode_texts

    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            logger.error("文档不存在: %s", doc_id)
            return

        # 从磁盘读取文件
        if not doc.file_path or not os.path.exists(doc.file_path):
            logger.error("文件不存在: %s", doc.file_path)
            doc.status = "failed"
            db.commit()
            return

        with open(doc.file_path, "rb") as f:
            content = f.read()

        # 更新状态
        doc.status = "processing"
        db.commit()
        logger.info("开始处理文档: %s, %d bytes", doc.filename, len(content))

        # 1. 解析文档
        text = parse_document(doc.filename, content)

        # 2. 文本切块
        chunks = chunk_text(text)

        # 3. 向量化
        vectors = encode_texts(chunks)

        # 4. 写入 Milvus
        vector_store.insert(doc.kb_id, doc_id, doc.filename, chunks, vectors)

        # 5. 更新文档状态
        doc.status = "done"
        doc.chunk_count = len(chunks)
        db.commit()

        logger.info("文档处理完成: %s, 切块数=%d", doc.filename, len(chunks))

    except Exception as e:
        logger.error("文档处理失败: doc_id=%s, error=%s", doc_id, e)
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.status = "failed"
            db.commit()
        raise

    finally:
        db.close()
