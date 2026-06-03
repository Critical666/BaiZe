"""共享 Base，确保所有模型注册到同一元数据。"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()

# 注册所有模型，确保 create_all 时自动建表
from app.models.user import User  # noqa: E402, F401
from app.models.knowledge_base import KnowledgeBase  # noqa: E402, F401
from app.models.document import Document  # noqa: E402, F401
from app.models.chat_history import ChatHistory  # noqa: E402, F401
