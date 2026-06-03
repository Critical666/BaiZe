"""Embedding 向量化服务，支持本地模型和 OpenAI API 两种模式。"""

import logging

import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)

# 全局模型单例，lazy 加载避免启动时耗时
_model = None


def _get_embedding_dim() -> int:
    """获取当前 Embedding 维度。"""
    if settings.embedding_provider == "openai":
        # text-embedding-3-small 默认 1536 维
        return 1536
    else:
        # paraphrase-multilingual-MiniLM-L12-v2 输出 384 维
        return 384


EMBEDDING_DIM = _get_embedding_dim()


def get_model():
    """获取全局 Embedding 模型单例（lazy 加载）。"""
    global _model
    if _model is None:
        if settings.embedding_provider == "openai":
            logger.info("使用 OpenAI Embedding API: %s", settings.openai_embedding_model)
            _model = {"type": "openai"}
        else:
            logger.info("加载本地 Embedding 模型: %s", settings.embedding_model)
            from sentence_transformers import SentenceTransformer

            _model = SentenceTransformer(settings.embedding_model)
            logger.info("本地 Embedding 模型加载完成")
    return _model


def encode_texts(texts: list[str]) -> np.ndarray:
    """
    将文本列表编码为向量矩阵。

    Args:
        texts: 待编码的文本列表。

    Returns:
        形状为 (len(texts), EMBEDDING_DIM) 的 numpy 数组。
    """
    model = get_model()

    if isinstance(model, dict) and model.get("type") == "openai":
        return _encode_openai(texts)
    else:
        return _encode_local(model, texts)


def encode_text(text: str) -> np.ndarray:
    """
    将单条文本编码为向量。

    Args:
        text: 待编码的文本。

    Returns:
        形状为 (1, EMBEDDING_DIM) 的 numpy 数组。
    """
    return encode_texts([text])


def _encode_local(model, texts: list[str]) -> np.ndarray:
    """使用本地 sentence-transformers 模型编码。"""
    vectors = model.encode(texts, normalize_embeddings=True)
    return np.array(vectors, dtype=np.float32)


def _encode_openai(texts: list[str]) -> np.ndarray:
    """使用 OpenAI Embedding API 编码。"""
    from openai import OpenAI

    client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )

    response = client.embeddings.create(
        model=settings.openai_embedding_model,
        input=texts,
    )

    vectors = [item.embedding for item in response.data]
    # 按 index 排序（OpenAI 不保证返回顺序）
    vectors = [v for _, v in sorted(zip([item.index for item in response.data], vectors))]

    return np.array(vectors, dtype=np.float32)
