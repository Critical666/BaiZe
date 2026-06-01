"""聊天服务（阶段 A2：完整 RAG 流程）。"""

import logging
import time

import numpy as np

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 384


class ChatService:
    """RAG 聊天服务。"""

    def chat(self, kb_id: str, data: ChatRequest) -> ChatResponse:
        """
        执行 RAG 检索 + LLM 回答（阶段 A2：简易版 LLM）。

        完整流程：问题向量化 → FAISS 检索 → Prompt 构建 → LLM 生成。
        """
        start = time.time()

        # 1. 问题向量化（使用简易哈希向量，后续换真实 Embedding）
        query_vector = self._encode(data.question)

        # 2. 向量检索
        chunks = vector_store.search(kb_id, query_vector, data.top_k)
        elapsed_search = time.time() - start
        logger.info(
            "RAG 检索完成: kb=%s, top_k=%d, 耗时=%.2fs, 结果=%d条",
            kb_id, data.top_k, elapsed_search, len(chunks),
        )

        # 3. 构建 Prompt
        if not chunks:
            return ChatResponse(answer="知识库中暂无相关文档，请先上传文档。", sources=[])

        context = "\n\n---\n\n".join(
            f"[来源: {c['filename']}]\n{c['text'][:800]}" for c in chunks
        )
        sources = [f"{c['filename']} (相似度: {c['distance']:.2f})" for c in chunks]

        # 4. LLM 生成（阶段 A2：简易模板回答）
        answer = self._generate_answer(data.question, context)

        elapsed_total = time.time() - start
        logger.info(
            "RAG 对话完成: 问题='%s', 来源=%d个, 总耗时=%.2fs",
            data.question[:50], len(sources), elapsed_total,
        )

        return ChatResponse(answer=answer, sources=sources)

    def _encode(self, text: str) -> np.ndarray:
        """
        文本向量化（阶段 A2：简易哈希向量）。

        后续可替换为 sentence-transformers 或 OpenAI Embedding API。
        """
        import hashlib
        h = hashlib.sha256(text.encode()).digest()
        # 将 32 字节哈希扩展为 384 维向量（通过重复填充）
        needed = EMBEDDING_DIM * 4  # 384 float32 = 1536 bytes
        expanded = (h * (needed // len(h) + 1))[:needed]
        vec = np.frombuffer(expanded, dtype=np.float32)[:EMBEDDING_DIM]
        # 归一化
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.reshape(1, -1)

    def _generate_answer(self, question: str, context: str) -> str:
        """
        LLM 生成回答（阶段 A2：简易关键词提取 + 模板）。

        后续可替换为 OpenAI / Claude API 调用。
        """
        lines = context.strip().split("\n")
        relevant_lines = []
        for line in lines:
            # 简单的相关性判断：包含问题中的关键词
            for word in question[:20]:
                if word in line and len(line) > 20:
                    relevant_lines.append(line)
                    break

        if not relevant_lines:
            # 返回上下文的开头部分
            relevant_lines = context[:500].split("\n")

        answer = "\n".join(relevant_lines[:10])
        return f"根据知识库文档，相关内容如下：\n\n{answer}\n\n（提示：当前为本地检索模式，连接 LLM 后可获得更智能的回答。）"
