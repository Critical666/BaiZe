"""FastAPI 应用入口。"""

from fastapi import FastAPI

app = FastAPI(
    title="BaiZe - RAG 知识库平台",
    description="白泽，通万物之情，晓天下之状。基于 RAG 的智能知识库系统。",
    version="0.1.0",
)
