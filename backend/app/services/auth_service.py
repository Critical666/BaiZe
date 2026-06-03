"""认证业务逻辑。"""

import uuid
import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin

logger = logging.getLogger(__name__)


class AuthService:
    """认证服务。"""

    def __init__(self, db: Session):
        self.db = db

    def register(self, data: UserCreate) -> dict:
        """注册新用户，角色固定为 user。"""
        existing = self.db.query(User).filter(
            (User.email == data.email) | (User.username == data.username)
        ).first()
        if existing:
            raise ValueError("邮箱或用户名已被注册")

        user = User(
            id=str(uuid.uuid4()),
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            role="user",
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        logger.info("新用户注册: %s (%s)", user.username, user.email)

        token = create_access_token(user.id, user.role)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "created_at": str(user.created_at),
            },
        }

    def login(self, data: UserLogin) -> dict:
        """用户登录，验证密码后返回 JWT。"""
        user = self.db.query(User).filter(User.email == data.email).first()
        if not user or not verify_password(data.password, user.password_hash):
            raise ValueError("邮箱或密码错误")

        logger.info("用户登录: %s", user.email)

        token = create_access_token(user.id, user.role)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "created_at": str(user.created_at),
            },
        }

    def update_role(self, user_id: str, new_role: str, operator_id: str) -> dict:
        """修改用户角色（仅管理员可调用）。"""
        if user_id == operator_id:
            raise ValueError("不能修改自己的角色")

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"用户 {user_id} 不存在")

        old_role = user.role
        user.role = new_role
        self.db.commit()
        self.db.refresh(user)
        logger.info("角色变更: %s (%s → %s), 操作者=%s", user.email, old_role, new_role, operator_id)
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "created_at": str(user.created_at),
        }

    def ensure_admin(self):
        """系统启动时调用，确保至少存在一个管理员。"""
        existing = self.db.query(User).filter(User.role == "admin").first()
        if existing:
            logger.info("管理员账户已存在，跳过初始化。")
            return

        logger.info("未检测到管理员账户，正在创建初始管理员...")
        admin = User(
            id=str(uuid.uuid4()),
            username=settings.init_admin_username,
            email=settings.init_admin_email,
            password_hash=hash_password(settings.init_admin_password),
            role="admin",
        )
        self.db.add(admin)
        self.db.commit()
        logger.info("初始管理员创建成功: %s", settings.init_admin_email)
