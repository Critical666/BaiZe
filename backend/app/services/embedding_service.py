"""Embedding 向量化服务，支持本地模型、OpenAI API 和简单哈希回退三种模式。"""

import hashlib
import logging

import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)

# 默认向量维度
_FALLBACK_DIM = 384

# 全局模型单例，lazy 加载避免启动时耗时
_model = None
_model_type = None  # "openai" | "local" | "fallback"


def _get_embedding_dim() -> int:
    """获取当前 Embedding 维度。"""
    if settings.embedding_provider == "openai":
        return 1536
    return _FALLBACK_DIM


EMBEDDING_DIM = _get_embedding_dim()


def get_model():
    """获取全局 Embedding 模型单例（lazy 加载）。"""
    global _model, _model_type
    if _model is not None:
        return _model

    if settings.embedding_provider == "openai":
        if settings.openai_api_key and settings.openai_api_key != "sk-your-openai-api-key":
            logger.info("使用 OpenAI Embedding API: %s", settings.openai_embedding_model)
            _model = {"type": "openai"}
            _model_type = "openai"
            return _model
        else:
            logger.warning("OpenAI API Key 未配置，降级到本地模型")

    # 尝试加载本地 sentence-transformers 模型
    try:
        from sentence_transformers import SentenceTransformer

        logger.info("加载本地 Embedding 模型: %s", settings.embedding_model)
        _model = SentenceTransformer(settings.embedding_model)
        _model_type = "local"
        logger.info("本地 Embedding 模型加载完成")
        return _model
    except Exception as e:
        logger.warning("本地 Embedding 模型加载失败: %s，使用哈希回退方案", e)
        _model = {"type": "fallback"}
        _model_type = "fallback"
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

    if _model_type == "openai":
        return _encode_openai(texts)
    elif _model_type == "local":
        return _encode_local(model, texts)
    else:
        return _encode_fallback(texts)


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


def _encode_fallback(texts: list[str]) -> np.ndarray:
    """
    哈希回退编码：基于文本哈希生成伪向量。

    当无法加载任何 Embedding 模型时使用，保证系统能端到端运行。
    生成的向量不具备语义相似性，仅用于开发调试。
    """
    logger.warning("使用哈希回退编码（无语义相似性，仅供开发调试）")
    vectors = []
    for text in texts:
        # 对文本进行多轮哈希，生成足够维度的向量
        vec = np.zeros(_FALLBACK_DIM, dtype=np.float32)
        for i in range(_FALLBACK_DIM):
            h = hashlib.sha256(f"{text}|{i}".encode("utf-8")).hexdigest()
            vec[i] = int(h[:8], 16) / 0xFFFFFFFF - 0.5
        # L2 归一化
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        vectors.append(vec)
    return np.array(vectors, dtype=np.float32)
