"""向量存储服务（Milvus Lite 嵌入式模式，零配置持久化）。"""

import logging
import os
import time

import uuid

import numpy as np
from pymilvus import MilvusClient

from app.services.embedding_service import EMBEDDING_DIM

logger = logging.getLogger(__name__)

MILVUS_DB_FILE = os.environ.get(
    "MILVUS_DB_FILE", "./milvus_data/baize.db"
)
COLLECTION_NAME = "knowledge_chunks"


class VectorStore:
    """向量存储（Milvus Lite，开发/小规模生产通用）。"""

    def __init__(self, dimension: int = EMBEDDING_DIM):
        self.dimension = dimension
        self.client = MilvusClient(MILVUS_DB_FILE)
        self._ensure_collection()

    def _ensure_collection(self):
        """确保 Collection 存在并已加载。"""
        collections = self.client.list_collections()
        if COLLECTION_NAME not in collections:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                dimension=self.dimension,
                metric_type="L2",
            )
            logger.info(
                "Milvus Lite Collection 已创建: %s, 维度=%d",
                COLLECTION_NAME,
                self.dimension,
            )
        # 每次启动/重启后需要将 Collection 加载到内存
        self.client.load_collection(COLLECTION_NAME)

    def insert(
        self,
        kb_id: str,
        doc_id: str,
        filename: str,
        chunks: list[str],
        vectors: np.ndarray,
    ):
        """
        批量插入向量和文本元数据。

        Args:
            kb_id: 知识库 ID。
            doc_id: 文档 ID。
            filename: 源文件名。
            chunks: 文本块列表。
            vectors: 向量数组 (n, dimension)。
        """
        data = []
        for i, (chunk, vec) in enumerate(zip(chunks, vectors)):
            data.append({
                "id": int(uuid.uuid4().int & 0x7FFFFFFFFFFFFFFF),
                "vector": vec.tolist(),
                "kb_id": kb_id,
                "doc_id": doc_id,
                "filename": filename,
                "text": chunk,
            })

        self.client.insert(
            collection_name=COLLECTION_NAME,
            data=data,
        )
        # 插入后刷新并重新加载，确保新数据可被检索
        self.client.flush(COLLECTION_NAME)
        self.client.release_collection(COLLECTION_NAME)
        self.client.load_collection(COLLECTION_NAME)
        logger.info("Milvus 向量插入完成: kb=%s, 块数=%d", kb_id, len(chunks))

    def search(self, kb_id: str, query_vector: np.ndarray, top_k: int = 5) -> list[dict]:
        """
        检索最相似的文本块。

        Args:
            kb_id: 知识库 ID（用于过滤）。
            query_vector: 查询向量 (1, dimension)。
            top_k: 返回结果数。

        Returns:
            包含 text、filename、distance 的结果列表。
        """
        start = time.time()
        results = self.client.search(
            collection_name=COLLECTION_NAME,
            data=[query_vector[0].tolist()],
            limit=top_k * 2,  # 多取一些再过滤 kb_id
            output_fields=["kb_id", "filename", "text"],
        )

        # 过滤指定知识库 + 截取 top_k
        hits = []
        for hit in results[0]:
            entity = hit.get("entity", {})
            if entity.get("kb_id") == kb_id:
                hits.append({
                    "text": entity.get("text", ""),
                    "filename": entity.get("filename", ""),
                    "distance": hit.get("distance", 0.0),
                })
            if len(hits) >= top_k:
                break

        elapsed = time.time() - start
        logger.info(
            "Milvus 检索完成: kb=%s, 结果=%d条, 耗时=%.2fs",
            kb_id, len(hits), elapsed,
        )
        return hits

    def delete_by_kb(self, kb_id: str):
        """删除知识库的所有向量数据。"""
        self.client.delete(
            collection_name=COLLECTION_NAME,
            filter=f'kb_id == "{kb_id}"',
        )
        logger.info("知识库 %s 的向量已清除", kb_id)


# 全局单例
vector_store = VectorStore()
