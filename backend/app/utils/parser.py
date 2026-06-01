"""文档解析器：支持 PDF / Word / Markdown / TXT。"""

import io
import logging

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".md", ".txt"}


def parse_document(filename: str, content: bytes) -> str:
    """
    根据文件扩展名解析文档内容，返回纯文本。

    Args:
        filename: 原始文件名（用于判断扩展名）。
        content: 文件二进制内容。

    Returns:
        提取的纯文本字符串。

    Raises:
        ValueError: 文件格式不支持时抛出。
    """
    ext = filename.lower()
    if ext.endswith(".pdf"):
        return _parse_pdf(content)
    if ext.endswith(".docx"):
        return _parse_docx(content)
    if ext.endswith(".md"):
        return content.decode("utf-8", errors="ignore")
    if ext.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")
    raise ValueError(f"不支持的文件格式: {filename}")


def _parse_pdf(content: bytes) -> str:
    """解析 PDF 文件。"""
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        raise ImportError("PyPDF2 未安装，无法解析 PDF")

    reader = PdfReader(io.BytesIO(content))
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    result = "\n".join(text_parts)
    logger.info("PDF 解析完成: %d 页, %d 字符", len(reader.pages), len(result))
    return result


def _parse_docx(content: bytes) -> str:
    """解析 Word 文档。"""
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx 未安装，无法解析 Word 文档")

    doc = Document(io.BytesIO(content))
    text_parts = [p.text for p in doc.paragraphs if p.text.strip()]
    result = "\n".join(text_parts)
    logger.info("Word 解析完成: %d 段落, %d 字符", len(text_parts), len(result))
    return result
