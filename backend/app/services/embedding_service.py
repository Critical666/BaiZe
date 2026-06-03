"""Embedding 向量化服务，基于 BGE-large-zh-v1.5 模型。

支持三种模式：
1. local — 本地 BGE 模型（默认，从 ModelScope/HuggingFace 加载）
2. openai — OpenAI Embedding API
3. fallback — 哈希伪向量（模型不可用时的降级方案）
"""

import hashlib
import logging
import os

import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)

# BGE-large-zh-v1.5 向量维度
BGE_DIM = 1024

# 全局模型单例，lazy 加载避免启动时耗时
_model = None
_model_type = None  # "openai" | "local" | "fallback"


def _get_embedding_dim() -> int:
    """获取当前 Embedding 维度。"""
    if settings.embedding_provider == "openai":
        return 1536
    return settings.embedding_dim


EMBEDDING_DIM = _get_embedding_dim()


def _resolve_model_path() -> str:
    """
    解析模型路径，优先从 ModelScope 本地缓存加载。

    Returns:
        模型本地路径或 HuggingFace 模型 ID。
    """
    model_name = settings.embedding_model

    # 优先检查 ModelScope 缓存目录
    modelscope_cache = os.path.join(
        os.path.expanduser("~"),
        ".cache",
        "modelscope",
        "BAAI",
    )
    if os.path.isdir(modelscope_cache):
        for entry in os.listdir(modelscope_cache):
            entry_path = os.path.join(modelscope_cache, entry)
            if not os.path.isdir(entry_path):
                continue
            # 检查目录下是否有模型文件（config.json + pytorch_model.bin）
            has_config = os.path.isfile(os.path.join(entry_path, "config.json"))
            has_model = os.path.isfile(
                os.path.join(entry_path, "pytorch_model.bin")
            ) or os.path.isfile(
                os.path.join(entry_path, "model.safetensors")
            )
            if has_config and has_model:
                logger.info("从 ModelScope 缓存加载模型: %s", entry_path)
                return entry_path

    # 回退到 HuggingFace 模型 ID（需要网络）
    logger.info("ModelScope 缓存未找到，使用 HuggingFace 模型 ID: %s", model_name)
    return model_name


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

        model_path = _resolve_model_path()
        logger.info("加载本地 Embedding 模型: %s", model_path)
        _model = SentenceTransformer(model_path)
        _model_type = "local"
        logger.info("本地 Embedding 模型加载完成，维度=%d", _model.get_embedding_dimension())
        return _model
    except Exception as e:
        logger.warning("本地 Embedding 模型加载失败: %s，使用哈希回退方案", e)
        _model = {"type": "fallback"}
        _model_type = "fallback"
        return _model


def encode_texts(texts: list[str]) -> np.ndarray:
    """
    将文本列表编码为向量矩阵（用于文档段落编码，不添加查询指令）。

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
    将单条文本编码为向量（用于查询编码，自动添加 BGE 查询指令）。

    BGE 模型的检索最佳实践：对查询添加指令前缀，对文档不添加。
    参考: https://huggingface.co/BAAI/bge-large-zh-v1.5

    Args:
        text: 待编码的查询文本。

    Returns:
        形状为 (1, EMBEDDING_DIM) 的 numpy 数组。
    """
    return encode_query(text)


def encode_query(query: str) -> np.ndarray:
    """
    将查询文本编码为向量（自动添加 BGE 查询指令）。

    对于 s2p（短查询检索长文档）场景，BGE 建议在查询前添加指令：
    "为这个句子生成表示以用于检索相关文章："
    文档段落不需要添加指令。

    Args:
        query: 用户的查询文本。

    Returns:
        形状为 (1, EMBEDDING_DIM) 的 numpy 数组。
    """
    model = get_model()

    # 拼接查询指令
    instructed_query = settings.embedding_query_instruction + query

    if _model_type == "openai":
        return _encode_openai([instructed_query])
    elif _model_type == "local":
        return _encode_local(model, [instructed_query])
    else:
        return _encode_fallback([instructed_query])


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
    dim = settings.embedding_dim
    vectors = []
    for text in texts:
        # 对文本进行多轮哈希，生成足够维度的向量
        vec = np.zeros(dim, dtype=np.float32)
        for i in range(dim):
            h = hashlib.sha256(f"{text}|{i}".encode("utf-8")).hexdigest()
            vec[i] = int(h[:8], 16) / 0xFFFFFFFF - 0.5
        # L2 归一化
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        vectors.append(vec)
    return np.array(vectors, dtype=np.float32)
