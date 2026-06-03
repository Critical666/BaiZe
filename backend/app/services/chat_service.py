"""聊天服务（阶段3：接入真实 Embedding + LLM）。"""

import logging
import time

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.vector_store import vector_store
from app.services.embedding_service import encode_text
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class ChatService:
    """RAG 聊天服务。"""

    def __init__(self, db=None):
        self.db = db

    def chat(self, kb_id: str, data: ChatRequest, user_id: str = None) -> ChatResponse:
        """
        执行完整 RAG 流程：问题向量化 → Milvus 检索 → LLM 生成。

        Args:
            kb_id: 知识库 ID。
            data: 聊天请求。
            user_id: 当前用户 ID（用于保存聊天记录）。

        Returns:
            包含回答和来源引用的响应。
        """
        start = time.time()

        # 1. 问题向量化
        query_vector = encode_text(data.question)

        # 2. 向量检索
        chunks = vector_store.search(kb_id, query_vector, data.top_k)
        elapsed_search = time.time() - start
        logger.info(
            "RAG 检索完成: kb=%s, top_k=%d, 耗时=%.2fs, 结果=%d条",
            kb_id, data.top_k, elapsed_search, len(chunks),
        )

        # 3. 无结果时直接返回
        if not chunks:
            answer = "知识库中暂无相关文档，请先上传文档。"
            if self.db and user_id:
                self._save_history(kb_id, user_id, data.question, answer, [])
            return ChatResponse(answer=answer, sources=[])

        # 4. 构建 Prompt 上下文
        context = "\n\n---\n\n".join(
            f"[来源: {c['filename']}]\n{c['text'][:800]}" for c in chunks
        )
        sources = [f"{c['filename']} (相似度: {c['distance']:.2f})" for c in chunks]

        # 5. LLM 生成回答
        answer = llm_service.generate(data.question, context)

        elapsed_total = time.time() - start
        logger.info(
            "RAG 对话完成: 问题='%s', 来源=%d个, 总耗时=%.2fs",
            data.question[:50], len(sources), elapsed_total,
        )

        # 6. 保存聊天记录
        if self.db and user_id:
            self._save_history(kb_id, user_id, data.question, answer, sources)

        return ChatResponse(answer=answer, sources=sources)

    def _save_history(self, kb_id: str, user_id: str, question: str, answer: str, sources: list[str]):
        """保存聊天记录到数据库。"""
        try:
            from app.services.chat_history_service import ChatHistoryService

            ChatHistoryService(self.db).save_chat(kb_id, user_id, question, answer, sources)
        except Exception as e:
            logger.error("保存聊天记录失败: %s", e)
