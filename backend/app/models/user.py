"""用户表 ORM 模型。"""

import uuid

from sqlalchemy import Column, String, DateTime, func
from app.models import Base


class User(Base):
    """用户表。"""

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(16), nullable=False, default="user")
    created_at = Column(DateTime, server_default=func.now())
