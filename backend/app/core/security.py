"""JWT 令牌生成与密码哈希验证。"""

from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """对明文密码进行 bcrypt 哈希。"""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """验证明文密码是否与哈希值匹配。"""
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str, role: str) -> str:
    """
    签发 JWT 访问令牌。

    Args:
        user_id: 用户 ID。
        role: 用户角色（admin / user）。

    Returns:
        JWT 字符串。
    """
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    """解析 JWT 令牌，返回 payload 字典。"""
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
