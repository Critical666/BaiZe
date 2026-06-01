"""文本切块工具：固定长度 + 重叠窗口。"""

import logging

logger = logging.getLogger(__name__)

CHUNK_SIZE = 500     # 每块字符数
CHUNK_OVERLAP = 50   # 相邻块重叠字符数


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    将长文本切分为固定大小的文本块（滑动窗口）。

    Args:
        text: 原始文本。
        chunk_size: 每块最大字符数。
        overlap: 相邻块之间的重叠字符数。

    Returns:
        文本块列表。
    """
    if not text.strip():
        return []

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap

    logger.info("文本切块完成: %d 字符 → %d 块", text_len, len(chunks))
    return chunks
