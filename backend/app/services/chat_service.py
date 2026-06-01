"""聊天服务（阶段 A：占位实现）。"""

from app.schemas.chat import ChatRequest, ChatResponse


class ChatService:
    """聊天服务（阶段 A：不调 LLM，阶段 A2 实现 RAG）。"""

    def chat(self, kb_id: str, data: ChatRequest) -> ChatResponse:
        """占位回答。阶段 A2 中接入向量检索 + LLM。"""
        return ChatResponse(
            answer=f"[RAG 模块待实现] 您的提问: {data.question}，知识库: {kb_id}",
            sources=[],
        )
