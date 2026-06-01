"""FastAPI 应用入口。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.endpoints import auth, knowledge, document, chat, stats
from app.core.database import engine, SessionLocal
from app.models import Base
from app.services.auth_service import AuthService

# 自动建表（开发阶段使用，生产环境应使用 Alembic）
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时创建初始管理员。"""
    db = SessionLocal()
    try:
        AuthService(db).ensure_admin()
    finally:
        db.close()
    yield


app = FastAPI(
    title="BaiZe - RAG 知识库平台",
    description="白泽，通万物之情，晓天下之状。基于 RAG 的智能知识库系统。",
    version="0.1.0",
    lifespan=lifespan,
)

# 挂载路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(knowledge.router, prefix="/api/v1")
app.include_router(document.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")

