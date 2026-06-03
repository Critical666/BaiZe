"""聊天记录数据模型。"""

from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func

from app.models import Base


class ChatHistory(Base):
    """聊天历史记录。"""

    __tablename__ = "chat_histories"

    id = Column(String, primary_key=True)
    kb_id = Column(String, ForeignKey("knowledge_bases.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(Text, nullable=False, default="[]")  # JSON 格式的来源列表
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
