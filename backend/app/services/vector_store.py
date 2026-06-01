"""向量存储服务：FAISS 开发模式，后续可切换 Milvus。

   设计为可替换接口：只需实现同样的 search() / insert() 方法即可切换后端。
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("faiss-cpu 未安装，向量检索将降级为关键词匹配")


class VectorStore:
    """向量存储（开发用 FAISS，生产换 Milvus）。"""

    def __init__(self, dimension: int = 384):
        """
        Args:
            dimension: 向量维度（与 embedding 模型匹配）。
        """
        self.dimension = dimension
        self.index = None
        self.chunks: list[dict] = []  # 存储文本元数据
        if FAISS_AVAILABLE:
            self.index = faiss.IndexFlatL2(dimension)
            logger.info("FAISS 向量索引已创建，维度=%d", dimension)

    def insert(self, kb_id: str, doc_id: str, filename: str, chunks: list[str], vectors: np.ndarray):
        """
        批量插入向量和文本元数据。

        Args:
            kb_id: 知识库 ID。
            doc_id: 文档 ID。
            filename: 源文件名。
            chunks: 文本块列表。
            vectors: 对应的向量数组 (n, dimension)。
        """
        if self.index is None:
            logger.warning("向量索引未初始化，降级存储文本")
            self.chunks.extend(
                {"kb_id": kb_id, "doc_id": doc_id, "filename": filename, "text": c}
                for c in chunks
            )
            return

        self.index.add(vectors.astype(np.float32))
        for chunk in chunks:
            self.chunks.append({
                "kb_id": kb_id,
                "doc_id": doc_id,
                "filename": filename,
                "text": chunk,
            })
        logger.info("向量插入完成: kb=%s, 块数=%d", kb_id, len(chunks))

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
        if self.index is None or self.index.ntotal == 0:
            # 降级：关键词匹配
            return self._keyword_search(kb_id, "", top_k)

        k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(query_vector.astype(np.float32), k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.chunks) and self.chunks[idx]["kb_id"] == kb_id:
                results.append({
                    "text": self.chunks[idx]["text"],
                    "filename": self.chunks[idx]["filename"],
                    "distance": float(dist),
                })

        logger.info("向量检索完成: kb=%s, 结果数=%d", kb_id, len(results))
        return results

    def _keyword_search(self, kb_id: str, query: str, top_k: int) -> list[dict]:
        """降级方案：简单的文本匹配。"""
        results = []
        for chunk in self.chunks:
            if chunk["kb_id"] == kb_id:
                results.append({
                    "text": chunk["text"],
                    "filename": chunk["filename"],
                    "distance": 0.0,
                })
        return results[:top_k]

    def delete_by_kb(self, kb_id: str):
        """删除知识库的所有向量（FAISS 不支持按 ID 删，需重建）。"""
        remaining = [c for c in self.chunks if c["kb_id"] != kb_id]
        self.chunks = remaining
        if self.index is not None and remaining:
            # 重建索引
            self.index = faiss.IndexFlatL2(self.dimension)
            logger.info("知识库 %s 的向量已清除", kb_id)


# 全局单例
vector_store = VectorStore()
