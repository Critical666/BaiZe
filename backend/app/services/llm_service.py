"""LLM 大语言模型服务，基于 OpenAI API。"""

import logging
import time

from app.core.config import settings

logger = logging.getLogger(__name__)

# RAG 系统提示词
RAG_SYSTEM_PROMPT = """你是白泽知识库助手，你的任务是根据提供的文档内容，准确、专业地回答用户的问题。

请遵循以下规则：
1. 仅基于提供的文档内容回答，不要编造或猜测信息。
2. 如果文档内容不足以回答问题，请明确说明"文档中暂未找到相关信息"。
3. 回答时引用信息来源，用 [来源: 文件名] 标注。
4. 使用简洁清晰的中文回答。
5. 如果问题涉及多个文档内容，请综合分析后给出完整回答。"""


class LLMService:
    """LLM 生成服务。"""

    def __init__(self):
        self._client = None

    def _get_client(self):
        """获取 OpenAI 客户端单例。"""
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )
        return self._client

    def generate(self, question: str, context: str) -> str:
        """
        基于 RAG 检索到的上下文生成回答。

        Args:
            question: 用户问题。
            context: 检索到的文档上下文文本。

        Returns:
            LLM 生成的回答文本。
        """
        if not settings.openai_api_key:
            logger.warning("OpenAI API Key 未配置，使用模板回退方案")
            return self._fallback_answer(question, context)

        start = time.time()
        try:
            client = self._get_client()

            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": RAG_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"参考文档内容：\n\n{context}\n\n---\n\n用户问题：{question}",
                    },
                ],
                temperature=0.3,
                max_tokens=2048,
            )

            answer = response.choices[0].message.content or ""
            elapsed = time.time() - start
            logger.info("LLM 回答生成完成，耗时=%.2fs，字数=%d", elapsed, len(answer))
            return answer

        except Exception as e:
            elapsed = time.time() - start
            logger.error("LLM 调用失败，耗时=%.2fs，error=%s", elapsed, e)
            return self._fallback_answer(question, context)

    def _fallback_answer(self, question: str, context: str) -> str:
        """OpenAI 不可用时的回退方案：提取相关段落。"""
        lines = context.strip().split("\n")
        relevant_lines = []
        for line in lines:
            for word in question[:20]:
                if word in line and len(line) > 20:
                    relevant_lines.append(line)
                    break

        if not relevant_lines:
            relevant_lines = context[:500].split("\n")

        answer = "\n".join(relevant_lines[:10])
        return (
            f"根据知识库文档，相关内容如下：\n\n{answer}\n\n"
            f"（提示：当前为本地检索模式，配置 LLM API 后可获得更智能的回答。）"
        )


# 全局单例
llm_service = LLMService()
