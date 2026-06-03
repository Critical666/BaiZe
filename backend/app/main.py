"""FastAPI 应用入口。"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.api.v1.endpoints import auth, knowledge, document, chat, stats
from app.core.database import engine, SessionLocal
from app.models import Base
from app.services.auth_service import AuthService

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def _migrate_schema():
    """开发阶段自动迁移：补充已存在表中缺失的列。"""
    inspector = inspect(engine)

    # documents 表：file_path 列（新增于文件落盘功能）
    if inspector.has_table("documents"):
        existing_cols = {col["name"] for col in inspector.get_columns("documents")}
        if "file_path" not in existing_cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE documents ADD COLUMN file_path VARCHAR(512)"))
                conn.commit()
            logger.info("Schema 迁移: documents 表新增 file_path 列")


# 自动建表 + 迁移（开发阶段使用，生产环境应使用 Alembic）
Base.metadata.create_all(bind=engine)
_migrate_schema()


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
    version="0.2.0",
    lifespan=lifespan,
)

# CORS 配置（开发阶段允许所有来源，生产环境应限制）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(knowledge.router, prefix="/api/v1")
app.include_router(document.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")

